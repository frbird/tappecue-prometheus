import yaml
import sys
import logging
import requests
import json
import time
from prometheus_client import Gauge, Info
from prometheus_client import start_http_server

# Loads variable from the YAML config file.  This is currently looing for tappecue_config.yaml
def load_vars(conf_file):
    with open(conf_file, 'r') as c:
        config_vars = yaml.safe_load(c)
    c.close()
    messages('Loaded config file.')
    return config_vars

# requires a URL, method and depending on the method headers or data.
def req(**kwargs):
    if kwargs['method'] == 'post':
        try:
            response = s.post(url = kwargs['url'], data = kwargs['data'])
            return response
        except:
            raise Exception(response.text)
    elif kwargs['method'] == 'get':
        try:
            response = s.get(url = kwargs['url'], headers = kwargs['headers'])
            return response
        except:
            raise Exception(response.text)

# Authenticate to Tappecue API
def authenticate (u, p):
    url = BASE_URL + "/login"
    data = {
        'username': u,
        'password': p
    }
    response = req(method='post', url=url, data=data)
    token = json.loads(response.text)
    if response.status_code == 200:
        messages('Authenticated to Tappecue API')
        return token
    else:
        messages('error: Authentication failed!')
        raise Exception(response.status_code)

# Returns any active Tappecue sessions
def getSession(token):
    headers = token
    url = BASE_URL + "/sessions"
    response = req(method='get', url=url, headers=headers)
    return json.loads(response.text)

# Pulls probe data for the given session
def getProbeData(token, id):
    headers = token
    url = BASE_URL + "/session/" + str(id)
    response = req(method='get', url=url, headers=headers)
    return json.loads(response.text)

# Creates a nested Dictionary with the session information and the probes data.
def normalize_data(sess_id, sess_name, pdata):
    metrics = {
        "session_name": sess_name,
        "session_id": sess_id,
        "probes": {}
        }
    for k, v in pdata.items():
        data = {
            k: v
            }
        metrics['probes'].update(data)
    return metrics

# Get metrics for each active Tappecue session and return a dictionary.  Requires session data to be a global var.
def get_data(token):
    session = getSession(token)
    if session:
        metrics = {}
        for s in session:
            if s['active'] == '1':
                id = s['id']
                name = s['name']
                pdata = getProbeData(token, id)
                metrics.update(normalize_data(id, name, pdata))
        messages('Got probe data')
        return metrics
    else:
        # Wait for a period of time before checking for an active session.  Default is 300 seconds (5 minutes).
        if NO_SESSION_DELAY:
            messages('No active sessions found.  Will check again in %s seconds.' % NO_SESSION_DELAY)
            time.sleep(NO_SESSION_DELAY)
        else:
            messages('No active sessions found.  Will check again in %s seconds.' % '300')
            time.sleep(300)

# Creates a Prom metric of type Gauge with a name, description and 4 labels (names only).
def create_gauges():
    g = Gauge('probe_data', 'Tappecue Probe Information', ['probe_num', 'name', 'role'])
    return(g)

# TODO create unit test using promtool.  Will need a test set of Tappecue data to use.
def update_gauges(metrics):
    if metrics:
        pd = metrics['probes']
        for p in pd:

            # These are label values that are applied to each metric below.
            labels = {
                "probe_num": p,
                "name": pd[p]['name'],
                "last_update": pd[p]['last_update'],
                "max_temp": pd[p]['max_temp'],
                "min_temp": pd[p]['min_temp'],
            }
            
            # sets the value for the metric.  Current temp versus min/max are tracked using coresponding labels.
            temps.labels(labels['probe_num'], labels['name'], 'curr_temp').set(pd[p]['current_temp'])
            temps.labels(labels['probe_num'], labels['name'], 'max_temp').set(pd[p]['max_temp'])
            temps.labels(labels['probe_num'], labels['name'], 'min_temp').set(pd[p]['min_temp']) 

        # Delay metrics retrieval for 'CHECK_DELAY' seconds if that var is defined.  If not delay for 30 seconds.
        if CHECK_DELAY:
            messages('Successfully updated Grafana.  Sleeping for %s seconds.' % CHECK_DELAY)
            time.sleep(CHECK_DELAY)
        else:
            messages('Successfully updated Grafana.  Sleeping for %s seconds.' % '30')
            time.sleep(30)

def messages(m):
    file_handler = logging.FileHandler(filename='tappecue.log')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]
    logging.basicConfig(
        level=logging.DEBUG, 
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=handlers
    )
    logger = logging.getLogger('tappecue')
    logger.info(m)

if __name__ == "__main__":
    # Initialize these vars so that "if" logic can be applied
    token = None
    temps = None
    conf_file = 'config.yaml'
    config = load_vars(conf_file)
    USER = config['tappecue_user']
    PSWD = config['tappecue_password']
    BASE_URL = config['tappecue_api_url']

    # Time in seconds between temp checks.
    CHECK_DELAY = config['check_probe_delay']

    # Time in seconds to check for a new session.
    NO_SESSION_DELAY = config['no_session_delay']

    start_http_server(8000)
    while True:
        if not token:
            # Configures a requests session so that only one HTTP connection is use versus one for each HTTP request.
            s = requests.session()
            token = authenticate(USER, PSWD)
        
        # Creates the actual Prom Gauge if it is not already present.
        if not temps:
            temps = create_gauges()
        update_gauges(get_data(token))

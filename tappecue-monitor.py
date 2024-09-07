import yaml
import sys
import os
import logging
import requests
import json
import time
from prometheus_client import Gauge, Info
from prometheus_client import start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)


# Loads variable from the YAML config file. This is currently looking for tappecue_config.yaml
def load_vars(conf_file: str) -> dict:
    try:
        with open(conf_file, 'r') as c:
            config_vars = yaml.safe_load(c)
        logging.info('Loaded config file.')
        return config_vars
    except FileNotFoundError:
        logging.error(f'Config file {conf_file} not found.')
        sys.exit(1)
    except yaml.YAMLError as e:
        logging.error(f'Error parsing YAML file: {e}')
        sys.exit(1)

# Requires a URL, method and depending on the method headers or data.
def req(method: str, url: str, headers: dict = None, data: dict = None) -> requests.Response:
    try:
        if method.lower() == 'post':
            response = requests.post(url, data=data)
        elif method.lower() == 'get':
            response = requests.get(url, headers=headers)
        else:
            raise ValueError(f'Unsupported method: {method}')
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logging.error(f'HTTP request failed: {e}')
        raise

# Authenticate to Tappecue API
def authenticate(u: str, p: str) -> dict:
    try:
        url = f'{BASE_URL}/login'
        data = {
            'username': u,
            'password': p
        }
        response = req(method='post', url=url, data=data)
        token = response.json()
        if response.status_code == 200:
            logging.info('Authenticated to Tappecue API')
            return token
        else:
            logging.error('Authentication failed!')
            raise Exception(response.status_code)
    except Exception as e:
        logging.error(f'Error authenticating to Tappecue: {e}')
        sys.exit(1)

# Returns any active Tappecue sessions
def getSession(token: dict) -> dict:
    headers = token
    url = f'{BASE_URL}/sessions'
    response = req(method='get', url=url, headers=headers)
    return response.json()

# Pulls probe data for the given session
def getProbeData(token: dict, id: str) -> dict:
    headers = token
    url = f'{BASE_URL}/session/{id}'
    response = req(method='get', url=url, headers=headers)
    return response.json()

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
            temps.labels(labels['probe_num'], labels['name'], 'curr_temp').set(pd[p]['current_temp'] or 0)
            temps.labels(labels['probe_num'], labels['name'], 'max_temp').set(pd[p]['max_temp'])
            temps.labels(labels['probe_num'], labels['name'], 'min_temp').set(pd[p]['min_temp']) 

        # Delay metrics retrieval for 'CHECK_DELAY' seconds if that var is defined.  If not delay for 30 seconds.
        if CHECK_DELAY:
            messages(f'Successfully updated Grafana.  Sleeping for {CHECK_DELAY} seconds.')
            time.sleep(CHECK_DELAY)
        else:
            sleep_time = 30
            messages(f'Successfully updated Grafana.  Sleeping for {sleep_time} seconds.')
            time.sleep(sleep_time)

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
    conf_file = os.getenv('CONFIG_FILE', 'config.yaml')
    config = load_vars(conf_file)
    USER = config['tappecue_user']
    PSWD = config['tappecue_password']
    BASE_URL = config['tappecue_api_url']
    LOG_LEVEL = config['logging_level']

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

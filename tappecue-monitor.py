import yaml
import sys
import logging
import requests
import json
from datetime import datetime
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


# Flattens the data returned from Tappecue and adds session_name, session_id and probe_id to each probe data set.
# def normalize_data(sess_id, sess_name, pdata):
#     metric_list = []
#     for k, v in pdata.items():
#         data = {
#         "session_name": sess_name,
#         "session_id": sess_id,
#         "probe_id": k,
#         }
#         data.update(v)
#         metric_list.append(data)
#     return metric_list

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

def create_gauges(d):
    # g = Gauge('temps', 'all probe temperatures', ['max_temp', 'min_temp', 'curr_temp', 'name'], )
    ct = Gauge('probe%s_curr_temp' % d, 'Probe %s - Current Temperature' % d, ['name'])
    max_t = Gauge('probe%s_max_temp' % d, 'Probe %s - Maximum Temperature' % d, ['name'])
    min_t = Gauge('probe%s_min_temp' % d, 'Probe %s - Minimum Temperature' % d, ['name'])
    # name = Info('probe%s_name' % d, 'Probe %s - Cook Info' % d)
    return(ct, max_t, min_t)#)

# TODO create unit test using promtool.  Will need a test set of Tappecue data to use.
def update_gauges(metrics):
    if metrics:
        pd = metrics['probes']
        for p in pd:
            labels = {
                "name": pd[p]['name'],
            }
            if p == '1':
                p1_gauge[0].labels(labels['name']).set(pd[p]['current_temp'])
                p1_gauge[1].labels(labels['name']).set(pd[p]['max_temp'])
                p1_gauge[2].labels(labels['name']).set(pd[p]['min_temp'])
                # p1_gauge[3].info({'probe_id': '1', 'probe_label': pd[p]['name']})
            elif p == '2':
                p2_gauge[0].labels(labels['name']).set(pd[p]['current_temp'])
                p2_gauge[1].labels(labels['name']).set(pd[p]['max_temp'])
                p2_gauge[2].labels(labels['name']).set(pd[p]['min_temp'])
                # p2_gauge[3].info({'probe_id': '2', 'probe_label': pd[p]['name']})
            elif p == '3':
                p3_gauge[0].labels(pd[p]['name']).set(pd[p]['current_temp'])
                p3_gauge[1].labels(labels['name']).set(pd[p]['max_temp'])
                p3_gauge[2].labels(labels['name']).set(pd[p]['min_temp'])
                # p3_gauge[3].info({'probe_id': '3', 'probe_label': pd[p]['name']})
            elif p == '4':
                p4_gauge[0].labels(labels['name']).set(pd[p]['current_temp'])
                p4_gauge[1].labels(labels['name']).set(pd[p]['max_temp'])
                p4_gauge[2].labels(labels['name']).set(pd[p]['min_temp'])
                # p4_gauge[3].info({'probe_id': '4', 'probe_label': pd[p]['name']})
        # Delay metrics retrieval for 't' seconds if that var is defined.  If not delay for 30 seconds.
        if CHECK_DELAY:
            messages('Successfully updated Grafana.  Sleeping for %s seconds.' % CHECK_DELAY)
            time.sleep(CHECK_DELAY)
        else:
            messages('Successfully updated Grafana.  Sleeping for %s seconds.' % '30')
            time.sleep(30)

def messages(m):
    # now = datetime.now()
    # sys.stdout.write(str(now) + ': %s \n' % m)
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
    conf_file = 'config.yaml'
    token = None
    config = load_vars(conf_file)
    USER = config['tappecue_user']
    PSWD = config['tappecue_password']
    BASE_URL = config['tappecue_api_url']
    # Time in seconds between temp checks.
    CHECK_DELAY = config['check_probe_delay']
    NO_SESSION_DELAY = config['no_session_delay']

    start_http_server(8000)
    while True:
        if not token:
            s = requests.session()
            token = authenticate(USER, PSWD)
        try:
            p1_gauge = create_gauges('1')
            p2_gauge = create_gauges('2')
            p3_gauge = create_gauges('3')
            p4_gauge = create_gauges('4')
        except:
            pass
        update_gauges(get_data(token))

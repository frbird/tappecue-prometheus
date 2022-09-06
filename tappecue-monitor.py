from logging import exception
import yaml
import sys
import requests
import json
from datetime import datetime
import time
from prometheus_client.core import Gauge, Info
from prometheus_client import start_http_server

conf_file = 'config.yaml'
# conf_file = 'tappecue/config.yaml'
now = datetime.now()

# Loads variable from the YAML config file.  This is currently looing for tappecue_config.yaml
def load_vars(conf_file):
    with open(conf_file, 'r') as c:
        config_vars = yaml.safe_load(c)
    c.close()
    messages('Loaded config file.')
    return config_vars

# Authenticate to Tappecue API
def authenticate (u, p):
    url = BASE_URL + "/login"
    data = {
        'username': u,
        'password': p
    }
    try:
        response = requests.post(url = url, data = data)
        # return response.text
        token = json.loads(response.text)
        if response.status_code == 200:
            messages('Authenticated to Tappecue API')
            return token
        else:
            messages('error: Authentication failed!')
            raise Exception(response.status_code)

    except:
        messages('Tappecue API authentication failed! \n\n')
        raise Exception(response.text)

# Returns any active Tappecue sessions
def getSession(token):
    headers = token
    url = BASE_URL + "/sessions"
    try:
        response = requests.get(url = url, headers = headers)
        return json.loads(response.text)
    except:
        raise Exception(response.text)

# Pulls probe data for the given session
def getProbeData(token, id):
    headers = token
    url = BASE_URL + "/session/" + str(id)
    try:
        response = requests.get(url = url, headers = headers)
        return json.loads(response.text)
    except:
        raise Exception(response.text)

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
    if session:
        metrics = {}
        for s in session:
            if s['active'] == '1':
                id = s['id']
                name = s['name']
                pdata = getProbeData(token, id)
                metrics.update(normalize_data(id, name, pdata))
        messages('Got probe data')
        messages(str(metrics))
        return metrics

# TODO Add Info metric for what is cooking.
def create_gauges(d):
    ct = Gauge('probe%s_curr_temp' % d, 'Probe %s - Current Temperature' % d)
    max_t = Gauge('probe%s_max_temp' % d, 'Probe %s - Maximum Temperature' % d)
    min_t = Gauge('probe%s_min_temp' % d, 'Probe %s - Minimum Temperature' % d)
    name = Info('probe%s_name' % d, 'Probe %s - Cook Info' % d)
    return(ct, max_t, min_t, name)

def update_gauges(metrics):
    if metrics:
        pd = metrics['probes']
        for p in pd:
            if p == '1':
                p1_gauge[0].set(pd[p]['current_temp'])
                p1_gauge[1].set(pd[p]['max_temp'])
                p1_gauge[2].set(pd[p]['min_temp'])
                p1_gauge[3].info({'Probe ID': '1', 'Probe Label': pd[p]['name']})
            elif p == '2':
                p2_gauge[0].set(pd[p]['current_temp'])
                p2_gauge[1].set(pd[p]['max_temp'])
                p2_gauge[2].set(pd[p]['min_temp'])
                p2_gauge[3].info({'Probe ID': '2', 'Probe Label': pd[p]['name']})
            elif p == '3':
                p3_gauge[0].set(pd[p]['current_temp'])
                p3_gauge[1].set(pd[p]['max_temp'])
                p3_gauge[2].set(pd[p]['min_temp'])
                p3_gauge[3].info({'Probe ID': '3', 'Probe Label': pd[p]['name']})
            elif p == '4':
                p4_gauge[0].set(pd[p]['current_temp'])
                p4_gauge[1].set(pd[p]['max_temp'])
                p4_gauge[2].set(pd[p]['min_temp'])
                p4_gauge[3].info({'Probe ID': '4', 'Probe Label': pd[p]['name']})
        messages('Successfully updated Grafana.  Sleeping for %s seconds.' % t)
        time.sleep(t)
        return metrics
    else:
        messages('No active sessions found.  Will check again in %s seconds.' % config['no_session_delay'])
        time.sleep(config['no_session_delay'])

def messages(m):
    sys.stdout.write(str(now) + ': %s \n' % m)

if __name__ == "__main__":
    token = None
    config = load_vars(conf_file)
    USER = config['tappecue_user']
    PSWD = config['tappecue_password']
    BASE_URL = config['tappecue_api_url']
    # Time in seconds between temp checks.
    t = config['check_probe_delay']
    start_http_server(8000)
    while True:
        if not token:
            token = authenticate(USER, PSWD)
        session = getSession(token)
        try:
            p1_gauge = create_gauges('1')
            p2_gauge = create_gauges('2')
            p3_gauge = create_gauges('3')
            p4_gauge = create_gauges('4')
        except:
            pass
        update_gauges(get_data(token))




# # Creates data format acceptible by Graphite.
# # TODO - Need to create real values for "interval".  Also, "tags" should be a dict.
# def create_graphite_metrics(data):
#     metric_list = []
#     for d in data:
#         if d['active'] == '1':
#             #Convert time string to int
#             time = datetime.strptime(d['last_update'], '%m/%d/%Y %I:%M:%S %p')
#             metric = {
#                 'name': d['name'] + ' - Current Temp',
#                 'metric': d['name'] + ' - Current Temp',
#                 "interval": 5,
#                 'value': float(d['current_temp']),
#                 'time': int(time.timestamp()),
#                 'mtype': 'count',
#                 # "tags": "probe_" + d['probe_id']
#             }
#             metric_list.append(metric)
#     return metric_list

# Function to write metrics to Graphite
# def write_graphite_metrics(metrics, url, user_id, apikey):
#     token = GRAFANA_USER + ":" + GRAFANA_APIKEY
#     headers = CaseInsensitiveDict()
#     headers["Accept"] = "application/json"
#     headers["Authorization"] = "Bearer %s" % token

#     # grafana_data.sort(key=lambda obj: obj['time'])
#     result = requests.post(url, json=metrics, headers=headers)
#     if result.status_code != 200:
#         raise Exception(result.text)
#     print('%s: %s' % (result.status_code, result.text))
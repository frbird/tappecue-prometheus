# TODO - update all the usage of the meesages function to use the logger object.  Specify a severity level for each message.

"""
Tappecue Monitor
This script monitors Tappecue sessions and retrieves probe data for active sessions.
It then creates Prometheus metricsbased on the retrieved data and updates Grafana with the metrics.
Author: Matt Castle
Usage:
    - Ensure that the Tappecue configuration file (config.yaml) is present in the same directory as this script.
    - Run the script to start monitoring Tappecue sessions and updating Grafana.
Requirements:
    - Python 3.x
    - config.yaml file with Tappecue API credentials and other configuration settings.
    - prometheus_client library
Functions:
    - load_vars(conf_file: str) -> dict:
        Loads variables from the YAML config file.
    - req(method: str, url: str, headers: dict = None, data: dict = None) -> requests.Response:
        Sends an HTTP request to the specified URL with the given method, headers, and data.
    - authenticate(u: str, p: str) -> dict:
        Authenticates to the Tappecue API using the provided username and password.
    - getSession(token: dict) -> dict:
        Retrieves information about active Tappecue sessions.
    - getProbeData(token: dict, id: str) -> dict:
        Retrieves probe data for a specific Tappecue session.
    - normalize_data(sess_id, sess_name, pdata) -> dict:
        Creates a nested dictionary with session information and probe data.
    - get_data(token) -> dict:
        Retrieves metrics for each active Tappecue session and returns a dictionary.
    - create_gauges() -> Gauge:
        Creates a Prometheus Gauge metric for Tappecue probe information.
    - update_gauges(metrics) -> None:
        Updates the Prometheus Gauges with the retrieved metrics.
    - messages(m, log_level) -> None:
        Logs messages to a file and stdout.
Main Execution:
    - Loads configuration variables from the config.yaml file.
    - Starts an HTTP server for Prometheus metrics.
    - Authenticates to the Tappecue API.
    - Creates Prometheus Gauges for probe data.
    - Continuously retrieves and updates metrics for active Tappecue sessions.
"""

import sys
import os
import logging
import time
import requests
import yaml
from prometheus_client import Gauge
from prometheus_client import start_http_server

# Configure a logger with a default level of 'INFO'.
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# Create log handlers.
formatter = logging.Formatter('[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')
file_handler = logging.FileHandler(filename='tappecue.log')
file_handler.setFormatter(formatter)
stdout_handler = logging.StreamHandler(stream=sys.stdout)
stdout_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

# Loads variable from the YAML config file. This is currently looking for tappecue_config.yaml
def load_vars(conf_file: str) -> dict:
    config = {}
    try:
        with open(conf_file, 'r') as c:
            config = yaml.safe_load(c)
        logger.info('Loaded config file.')
    except (FileNotFoundError, PermissionError) as e:
        logger.error(f'Error reading config file {conf_file}: {e}. If Environment variables are set you can ignore this error.')
    except yaml.YAMLError as e:
        logger.error(f'Error parsing YAML file: {e}.')

    # Load API configuration variables
    try:
        USER = os.getenv('TAPPECUE_USER', config.get('tappecue_user'))
        PSWD = os.getenv('TAPPECUE_PASSWORD', config.get('tappecue_password'))
        BASE_URL = os.getenv('TAPPECUE_API_URL', config.get('tappecue_api_url', 'https://tappecue.babyvelociraptor.com'))

        # Time in seconds between temp checks.
        CHECK_DELAY = int(os.getenv('CHECK_PROBE_DELAY', config.get('check_probe_delay', 60)))

        # Time in seconds to check for a new session.
        NO_SESSION_DELAY = int(os.getenv('NO_SESSION_DELAY', config.get('no_session_delay', 1200)))

        # Disable SSL verification if set to False.
        VERIFY_SSL = None
        ssl_check = os.getenv('VERIFY_SSL', config.get('verify_ssl')).lower()
        if ssl_check.lower() in ['false', 'no', 'off', '0']:
            VERIFY_SSL = False
        else:
            VERIFY_SSL = True

    except Exception as e:
        logger.error(f'Error loading configuration variables: {e}')

    return {
        'user': USER,
        'password': PSWD,
        'base_url': BASE_URL,
        'check_delay': CHECK_DELAY,
        'no_session_delay': NO_SESSION_DELAY,
        'verify_ssl': VERIFY_SSL
    }

# Requires a URL, method and depending on the method headers or data.
def req(method: str, url: str, headers: dict = None, data: dict = None, verify=None) -> requests.Response:
    logger.debug(f'Request info:\nurl: {url}\nmethod: {method}\nheaders: {headers}\ndata: {data}\nverify: {verify}\n')
    try:
        if method.lower() == 'post':
            response = requests.post(url, data=data, verify=verify)
        elif method.lower() == 'get':
            response = requests.get(url, headers=headers, verify=verify)
        else:
            raise ValueError(f'Unsupported method: {method}')
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f'HTTP request failed: {e}')
        raise

# Authenticate to Tappecue API
def authenticate(u: str, p: str) -> dict:
    try:
        url = f'{config["base_url"]}/login'
        data = {
            'username': u,
            'password': p
        }
        response = req(method='post', url=url, data=data, verify=config["verify_ssl"])
        token = response.json()
        if response.status_code == 200:
            logger.info('Authenticated to Tappecue API')
            return token
        else:
            logger.error('Authentication failed!')
            raise Exception(response.status_code)
    except Exception as e:
        logger.error(f'Error authenticating to Tappecue: {e}')
        sys.exit(1)

# Returns any active Tappecue sessions
def getSession(token: dict) -> dict:
    headers = token
    url = f'{config["base_url"]}/sessions'
    response = req(method='get', url=url, headers=headers, verify=config["verify_ssl"])
    return response.json()

# Pulls probe data for the given session
def getProbeData(token: dict, id: str) -> dict:
    headers = token
    url = f'{config["base_url"]}/session/{id}'
    response = req(method='get', url=url, headers=headers, verify=config["verify_ssl"])
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
        logger.info('Got probe data')
        return metrics
    else:
        # Wait for a period of time before checking for an active session.  Default is 300 seconds (5 minutes).
        if config["no_session_delay"]:
            logger.info(f'No active sessions found.  Will check again in {config.get("no_session_delay")} seconds.')
            time.sleep(config["no_session_delay"])
        else:
            logger.error(f'No value set for {config["no_session_delay"]}.')

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
        if config["check_delay"]:
            logger.info(f'Successfully updated Grafana.  Sleeping for {config["check_delay"]} seconds.')
            time.sleep(config["check_delay"])
        else:
            logger.error(f'No value found for {config["check_delay"]}.')

if __name__ == "__main__":
    # Initialize these vars so that "if" logic can be applied
    token = None
    temps = None

    conf_file = os.getenv('CONFIG_FILE', 'config.yaml')
    config = load_vars(conf_file)

    start_http_server(8000)
    while True:
        if not token:
            # Configures a requests session so that only one HTTP connection is use versus one for each HTTP request.
            s = requests.session()
            token = authenticate(config["user"], config["password"])
        
        # Creates the actual Prom Gauge if it is not already present.
        if not temps:
            temps = create_gauges()
        update_gauges(get_data(token))

# Testing CI/CD pipeline

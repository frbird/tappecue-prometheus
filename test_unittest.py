import pytest
import os
import yaml
import requests
from unittest.mock import patch, mock_open
from tappecue_monitor import load_vars, req

# Check to be sure FileNotFoundError is raised when the file is not found.
def test_load_vars_file_not_found(caplog):
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            load_vars("config.yaml")
        assert "Error reading config file" in caplog.text

def test_load_vars_yaml_error(caplog):
    invalid_yaml_content = """
    tappecue_user "user"
    tappecue_api_url: 
    "http://example.com"
    """
    with patch("builtins.open", mock_open(read_data=invalid_yaml_content)):
        with pytest.raises(yaml.YAMLError):
            load_vars("config.yaml")
        assert "Error parsing YAML file" in caplog.text

def test_load_environment_vars():
    mock_yaml_content = """
    tappecue_user: "yaml_user"
    tappecue_password: "yaml_password"
    tappecue_api_url: "yaml-http://example.com"
    log_level: "yaml-INFO"
    check_probe_delay: "yaml-30"
    no_session_delay: "yaml-60"
    """
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        os.environ["TAPPECUE_USER"] = "user"
        os.environ["TAPPECUE_PASSWORD"] = "password"
        os.environ["TAPPECUE_API_URL"] = "http://example.com"
        os.environ["LOGGING_LEVEL"] = "INFO"
        os.environ["CHECK_PROBE_DELAY"] = "30"
        os.environ["NO_SESSION_DELAY"] = "60"
        os.environ["LOG_LEVEL"] = "INFO"
        config = load_vars("config.yaml")
        assert config["user"] == "user"
        assert config["password"] == "password"
        assert config["base_url"] == "http://example.com"
        assert config["log_level"] == "INFO"
        assert config["check_delay"] == 30
        assert config["no_session_delay"] == 60

def test_load_config_file_vars():
    mock_yaml_content = """
    tappecue_user: "yaml_user"
    tappecue_password: "yaml_password"
    tappecue_api_url: "yaml-http://example.com"
    log_level: "yaml-INFO"
    check_probe_delay: "30"
    no_session_delay: "60"
    """
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        config = load_vars("config.yaml")
        assert config["user"] == "yaml_user"
        assert config["password"] == "yaml_password"
        assert config["base_url"] == "yaml-http://example.com"
        assert config["log_level"] == "yaml-INFO"
        assert config["check_delay"] == 30
        assert config["no_session_delay"] == 60

# Test req function
def test_req_get_success():
    with patch("requests.get") as mock_get:
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        response = req("get", "http://example.com")
        assert response.status_code == 200

def test_req_post_success():
    with patch("requests.post") as mock_post:
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        response = req("post", "http://example.com", data={"key": "value"})
        assert response.status_code == 200

def test_req_unsupported_method():
    with pytest.raises(ValueError):
        req("put", "http://example.com")

def test_req_http_error():
    with patch("requests.get") as mock_get:
        mock_response = requests.Response()
        mock_response.status_code = 404
        mock_response.raise_for_status = lambda: (_ for _ in ()).throw(requests.HTTPError)
        mock_get.return_value = mock_response
        with pytest.raises(requests.HTTPError):
            req("get", "http://example.com")
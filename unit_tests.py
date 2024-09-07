import pytest
import os
import sys
import yaml
import requests
from unittest.mock import patch, mock_open
from tappecue_monitor import load_vars, req

# Test load_vars function
def test_load_vars_success():
    mock_yaml_content = """
    tappecue_user: "user"
    tappecue_password: "password"
    tappecue_api_url: "http://example.com"
    logging_level: "INFO"
    check_probe_delay: 30
    no_session_delay: 60
    """
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        config = load_vars("config.yaml")
        assert config["tappecue_user"] == "user"
        assert config["tappecue_password"] == "password"
        assert config["tappecue_api_url"] == "http://example.com"
        assert config["logging_level"] == "INFO"
        assert config["check_probe_delay"] == 30
        assert config["no_session_delay"] == 60

def test_load_vars_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(SystemExit):
            load_vars("config.yaml")

def test_load_vars_yaml_error():
    with patch("builtins.open", side_effect=yaml.YAMLError):
        with pytest.raises(SystemExit):
            load_vars("config.yaml")

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
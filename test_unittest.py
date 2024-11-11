# TODO - Add test cases for more functions

import pytest
import os
import yaml
from unittest.mock import patch, mock_open
from tappecue_monitor import load_vars

def test_load_vars_success():
    mock_yaml_content = """
    tappecue_user: "user"
    tappecue_password: "password"
    tappecue_api_url: "http://example.com"
    check_probe_delay: 30
    no_session_delay: 60
    """
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        config = load_vars("config.yaml")
        assert config["user"] == "user"
        assert config["password"] == "password"
        assert config["base_url"] == "http://example.com"
        assert config["check_delay"] == 30
        assert config["no_session_delay"] == 60

# def test_load_vars_file_not_found(caplog):
   

# def test_load_vars_yaml_error(caplog):
#     with patch("builtins.open", mock_open(read_data="invalid_yaml")):
#         with patch("yaml.safe_load", side_effect=yaml.YAMLError("mocked error")):
#             config = load_vars("config.yaml")
#             assert "Error parsing YAML file" in caplog.text
#             assert config["user"] == "default_user"
#             assert config["password"] == "default_password"
#             assert config["base_url"] == "http://default-url.com"
#             assert config["check_delay"] == 30
#             assert config["no_session_delay"] == 60
#             assert config["log_level"] == "INFO"

def test_load_environment_vars():
    mock_yaml_content = """
    tappecue_user: "yaml_user"
    tappecue_password: "yaml_password"
    tappecue_api_url: "yaml-http://example.com"
    log_level: "yaml-INFO"
    check_probe_delay: 30
    no_session_delay: 60
    """
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        os.environ["TAPPECUE_USER"] = "env_user"
        os.environ["TAPPECUE_PASSWORD"] = "env_password"
        os.environ["TAPPECUE_API_URL"] = "env-http://example.com"
        os.environ["LOG_LEVEL"] = "env-INFO"
        os.environ["CHECK_PROBE_DELAY"] = "40"
        os.environ["NO_SESSION_DELAY"] = "70"
        config = load_vars("config.yaml")
        assert config["user"] == "env_user"
        assert config["password"] == "env_password"
        assert config["base_url"] == "env-http://example.com"
        assert config["check_delay"] == 40
        assert config["no_session_delay"] == 70
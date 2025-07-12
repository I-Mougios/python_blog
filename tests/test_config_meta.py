import importlib
import json
from pathlib import Path

import pytest

config_meta_module = importlib.import_module("src.2025.July.config_meta")
dispatch_module = importlib.import_module("src.2025.July.dispatch")

ConfigMeta = config_meta_module.ConfigMeta
Dispatcher = dispatch_module.Dispatcher


# ---------------------- Fixture preparation ----------------
@Dispatcher
def create_resource(fn: str):
    config_directory = Path(__file__).parent
    config_name = "configs.ini"
    config_path = config_directory / config_name
    lines = [
        "[Globals]",
        "log_level = INFO",
        "timeout = 30",
        "retries = 3\n",
        "[database]",
        "host = localhost",
        "port = 5432",
        "username = admin",
        "password = secret",
        "log_level = DEBUG\n",
        "[api]",
        "endpoint = /v1/resources",
        "token = abc123",
        "timeout = 10",
    ]
    config_path.write_text("\n".join(lines))

    return config_directory, config_name, config_path


@create_resource.register("test_getter_json")
def _(fn: str):
    config_directory = Path(__file__).parent
    config_name = "configs.json"
    config_path = config_directory / config_name

    config_dict = {
        "Globals": {"log_level": "INFO", "timeout": "30", "retries": "3"},
        "database": {
            "host": "localhost",
            "port": "5432",
            "username": "admin",
            "password": "secret",
            "log_level": "DEBUG",
        },
        "api": {"endpoint": "/v1/resources", "token": "abc123", "timeout": "10"},
    }

    config_path.write_text(json.dumps(config_dict, indent=2))
    return config_directory, config_name, config_path


@create_resource.register("test_ini_without_globals")
def _(fn: str):
    config_directory = Path(__file__).parent
    config_name = "configs.ini"
    config_path = config_directory / config_name
    lines = [
        "[database]",
        "host = localhost",
        "port = 5432\n",
        "[api]",
        "endpoint = /v1/resources",
        "token = abc123",
        "timeout = 10",
    ]
    config_path.write_text("\n".join(lines))
    return config_directory, config_name, config_path


@create_resource.register("test_json_without_globals")
def _(fn: str):
    config_directory = Path(__file__).parent
    config_name = "configs.json"
    config_path = config_directory / config_name
    config_dict = {
        "database": {"host": "localhost", "port": "5432"},
        "api": {"endpoint": "/v1/resources", "token": "abc123", "timeout": "10"},
    }
    config_path.write_text(json.dumps(config_dict, indent=2))
    return config_directory, config_name, config_path


# ----------------------- Fixture ---------------------
@pytest.fixture(scope="function")
def resource(request):
    test_name = request.node.name
    print(f"\n[SETUP] Fixture called for test: {test_name}")
    config_directory, config_name, config_path = create_resource(test_name)
    yield config_directory, config_name, config_path

    print(f"[TEARDOWN] Cleaning up file for test: {test_name}\n")
    config_path.unlink()
    try:
        config_directory.rmdir()
    except OSError:
        pass


# -------------------- TESTS ---------------------------
def test_getter(resource):
    config_directory, config_name, _ = resource

    class Config(metaclass=ConfigMeta, config_directory=config_directory, config_filename=config_name):
        pass

    assert Config.database.host == "localhost"  # base scenario
    assert Config.api.get("log_level") == "INFO"  # base scenario of get() method
    assert Config.database.get("log_level") == "DEBUG"  # local configs take precedence of global configs
    assert Config.database.log_level == "DEBUG"  # local configs take precedence of global configs
    assert Config.database.get("port", default=5432) == "5432"  # default not used since port exists in global section
    assert Config.database.get("port", cast=int) == 5432  # "cast" is applied to the value
    assert Config.api.get("missing_key", default="missing") == "missing"  # default value when key is missing completely
    assert Config.api.get("port", default="8000", cast=int) == 8000  # cast function applied to default value


def test_getter_json(resource):
    config_directory, config_name, _ = resource

    class Config(metaclass=ConfigMeta, config_directory=config_directory, config_filename=config_name):
        pass

    assert Config.database.host == "localhost"
    assert Config.api.get("log_level") == "INFO"
    assert Config.database.get("log_level") == "DEBUG"
    assert Config.database.log_level == "DEBUG"
    assert Config.database.get("port", default=5432) == "5432"
    assert Config.database.get("port", cast=int) == 5432
    assert Config.api.get("missing_key", default="missing") == "missing"
    assert Config.api.get("port", default="8000", cast=int) == 8000


def test_ini_without_globals(resource):
    config_directory, config_name, _ = resource

    class Config(metaclass=ConfigMeta, config_directory=config_directory, config_filename=config_name):
        pass

    assert Config.database.host == "localhost"
    assert Config.api.get("log_level", default="INFO") == "INFO"  # fallback to default
    assert Config.database.get("log_level", default="DEBUG") == "DEBUG"  # default only
    assert Config.api.get("timeout", cast=int) == 10
    assert Config.api.timeout == "10"
    assert Config.database.get("retries", cast=int) is None


def test_json_without_globals(resource):
    config_directory, config_name, _ = resource

    class Config(metaclass=ConfigMeta, config_directory=config_directory, config_filename=config_name):
        pass

    assert Config.api.endpoint == "/v1/resources"
    assert Config.api.get("log_level", default="INFO") == "INFO"
    assert Config.database.get("port", cast=int) == 5432
    assert Config.database.get("retries", default="3") == "3"
    assert Config.database.get("retries", cast=int) is None  # it will not fail but it will return the default

import os
import json
import pytest

from app.cloudfoundry_config import extract_cloudfoundry_config, set_config_env_vars


@pytest.fixture
def postgres_config():
    return [
        {
            'credentials': {
                'uri': 'postgres uri'
            }
        }
    ]


@pytest.fixture
def postgresql_config():
    return [
        {
            'credentials': {
                'MASTER_USERNAME': 'u',
                'MASTER_PASSWORD': 'pass+word',
                'ENDPOINT_ADDRESS': 'a',
                'PORT': '1',
                'DB_NAME': 'd',
            }
        }
    ]


@pytest.fixture
def cloudfoundry_postgresql_config(postgresql_config):
    return {
        'postgresql': postgresql_config,
        'user-provided': []
    }


@pytest.fixture
def cloudfoundry_postgresql_environ(monkeypatch, cloudfoundry_postgresql_config):
    monkeypatch.setenv('VCAP_SERVICES', json.dumps(cloudfoundry_postgresql_config))
    monkeypatch.setenv('VCAP_APPLICATION', '{"space_name": "🚀🌌"}')


@pytest.mark.usefixtures('os_environ', 'cloudfoundry_postgresql_environ')
def test_extract_cloudfoundry_postgresql_config_populates_other_vars():
    extract_cloudfoundry_config()

    assert os.environ['SQLALCHEMY_DATABASE_URI'] == 'postgresql://u:pass%2Bword@a:1/d'


@pytest.fixture
def cloudfoundry_config(postgres_config):
    return {
        'postgres': postgres_config,
        'user-provided': []
    }


@pytest.fixture
def cloudfoundry_environ(monkeypatch, cloudfoundry_config):
    monkeypatch.setenv('VCAP_SERVICES', json.dumps(cloudfoundry_config))
    monkeypatch.setenv('VCAP_APPLICATION', '{"space_name": "🚀🌌"}')


@pytest.mark.usefixtures('os_environ', 'cloudfoundry_environ')
def test_extract_cloudfoundry_config_populates_other_vars():
    extract_cloudfoundry_config()

    assert os.environ['SQLALCHEMY_DATABASE_URI'] == 'postgres uri'


@pytest.mark.usefixtures('os_environ', 'cloudfoundry_environ')
def test_set_config_env_vars_ignores_unknown_configs(cloudfoundry_config):
    cloudfoundry_config['foo'] = {'credentials': {'foo': 'foo'}}
    cloudfoundry_config['user-provided'].append({
        'name': 'bar', 'credentials': {'bar': 'bar'}
    })

    set_config_env_vars(cloudfoundry_config)

    assert 'foo' not in os.environ
    assert 'bar' not in os.environ

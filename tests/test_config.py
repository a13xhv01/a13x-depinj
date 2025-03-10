"""
Test suite for the Config class in a13x_depinj.config module.

This module contains comprehensive tests for the configuration management system,
including tests for:
- Singleton pattern implementation
- YAML config file loading and validation
- Config value retrieval with dot notation
- Thread safety
- Configuration immutability
- Environment variable overrides
- Error handling for invalid configs and missing files

Author: a13x.h.cc@gmail.com

MIT License

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

DISCLAIMER:
This software is provided for educational and testing purposes only. 
The author assumes no liability for any damages or losses arising from the use
of this software. Use at your own risk.
"""

import os
from pathlib import Path
import pytest
import yaml
from unittest.mock import patch, mock_open

# I am getting the error: ImportError: attempted relative import beyond top-level package
# what could be the problem?
from a13x_depinj.config import Config
from a13x_depinj.errors import ConfigurationError, ConfigDiscoveryError

@pytest.fixture
def sample_config():
    return {
        'app': {
            'name': 'test_app',
            'version': '1.0.0'
        },
        'database': {
            'url': 'localhost',
            'port': 5432
        }
    }

@pytest.fixture
def config_file(tmp_path, sample_config):
    config_path = tmp_path / 'config.yaml'
    config_path.write_text(yaml.dump(sample_config))
    return config_path

@pytest.fixture
def config_instance(config_file):
    config = Config.load_config(config_file)
    yield config
    Config._config.clear()
    Config._instance = None
    Config._initialized = False

def test_singleton_pattern():
    config1 = Config()
    config2 = Config()
    assert config1 is config2

def test_load_config_from_file(config_file, sample_config):
    config = Config.load_config(config_file)
    assert config._config == sample_config

def test_load_config_invalid_yaml():
    mock_content = """
    invalid: yaml: content:
      - this is not valid yaml
          wrong indentation
    """
    with patch('pathlib.Path.read_text', return_value=mock_content):
        with pytest.raises(ConfigurationError):
            Config.load_config('dummy.yaml')

def test_load_config_file_not_found():
    with patch('pathlib.Path.is_file', return_value=False):
        with pytest.raises(ConfigDiscoveryError):
            Config.load_config('nonexistent.yaml')

def test_get_existing_value(config_instance):
    value = config_instance.get('app.name')
    assert value == 'test_app'

def test_get_nested_value(config_instance):
    value = config_instance.get('database.port')
    assert value == 5432

def test_get_nonexistent_value(config_instance):
    value = config_instance.get('nonexistent.path')
    assert value is None

def test_get_with_default(config_instance):
    value = config_instance.get('nonexistent.path', 'default')
    assert value == 'default'

def test_get_entire_config(config_instance, sample_config):
    config = config_instance.get_config()
    assert config == sample_config
    assert config is not sample_config  # Should be a deep copy

def test_reload_config(tmp_path):
    # Create initial config
    config_path = tmp_path / 'config.yaml'
    config_path.write_text(yaml.dump({'initial': 'config'}))
    
    config = Config.load_config(config_path)
    assert config.get('initial') == 'config'
    
    # Write new config
    config_path.write_text(yaml.dump({'new': 'config'}))
    
    # Clear all configuration state
    Config.clear_config()
    
    # Reload config
    config = Config.load_config(config_path)
    assert config.get('new') == 'config'

def test_thread_safety():
    import threading
    configs = []
    
    def get_config():
        configs.append(Config())
    
    threads = [threading.Thread(target=get_config) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert all(c is configs[0] for c in configs)

def test_validate_config_invalid_type():
    with pytest.raises(ConfigurationError):
        Config._validate_config(['invalid', 'config'])

@pytest.mark.parametrize('path,expected', [
    ('app.name', 'test_app'),
    ('database.port', 5432),
    ('invalid.path', None),
    ('', None),
    (None, None)
])
def test_get_various_paths(config_instance, path, expected):
    assert config_instance.get(path) == expected

def test_config_immutability(config_instance):
    config = config_instance.get_config()
    config['app']['name'] = 'modified'
    
    assert config_instance.get('app.name') == 'test_app'

def test_environment_variable_override(tmp_path):
    # Create config file in temp directory
    config_dir = tmp_path / 'config'
    config_dir.mkdir()
    config_path = config_dir / 'env_config.yaml'
    config_path.write_text(yaml.dump({'env': 'test'}))
    
    with patch.dict(os.environ, {'APP_CONFIG_DIR': str(config_dir)}):
        config = Config.load_config('env_config.yaml')
        assert config.get('env') == 'test'
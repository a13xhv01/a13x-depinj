"""
Tests for the ComponentRegistry class in the a13x_depinj package.

This module contains comprehensive test cases for the ComponentRegistry functionality,
including component registration, initialization, cleanup, YAML configuration loading,
and error handling. Tests cover singleton pattern, lazy loading, component lifecycle,
and various edge cases.

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

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import yaml

from a13x_depinj.registry import ComponentRegistry
from a13x_depinj.config import Config
from a13x_depinj.errors import (
    ComponentNotFoundError,
    ComponentInitializationError,
    InvalidConfigurationError,
    RegistryError
)

class MockComponent:
    def __init__(self, config):
        self.config = config
        self.initialized = True

class MockComponentWithCleanup(MockComponent):
    def cleanup(self):
        self.initialized = False

class FailingComponent:
    def __init__(self, config):
        raise ValueError("Initialization failed")

@pytest.fixture
def registry():
    registry = ComponentRegistry()
    yield registry
    registry._components.clear()
    registry._configs.clear()
    registry._initialized.clear()
    ComponentRegistry._instances.clear()

@pytest.fixture
def sample_yaml():
    return {
        'components': [
            {
                'module': 'tests.test_registry',
                'class': 'MockComponent',
                'config_path': 'test.config'
            }
        ]
    }

@pytest.fixture
def yaml_file(tmp_path, sample_yaml):
    path = tmp_path / 'deployment.yaml'
    path.write_text(yaml.dump(sample_yaml))
    return path

@pytest.fixture
def config():
    return Mock(spec=Config)

def test_singleton_pattern():
    registry1 = ComponentRegistry()
    registry2 = ComponentRegistry()
    assert registry1 is registry2

def test_register_component(registry):
    registry.register(MockComponent, {'key': 'value'})
    component = registry.get(MockComponent)
    assert isinstance(component, MockComponent)
    assert component.config == {'key': 'value'}

def test_register_component_lazy(registry):
    registry.register(MockComponent, {'key': 'value'}, lazy=True)
    assert MockComponent not in registry._components
    assert not registry._initialized.get(MockComponent, False)
    
    component = registry.get(MockComponent)
    assert isinstance(component, MockComponent)
    assert component.config == {'key': 'value'}
    assert registry._initialized[MockComponent]

def test_component_cleanup(registry):
    component_class = MockComponentWithCleanup
    registry.register(component_class, {})
    component = registry.get(component_class)
    assert component.initialized
    
    registry.unregister(component_class)
    assert not component.initialized

def test_get_unregistered_component(registry):
    with pytest.raises(ComponentNotFoundError):
        registry.get(MockComponent)

def test_failing_component_initialization(registry):
    with pytest.raises(ComponentInitializationError):
        registry.register(FailingComponent, {})

def test_from_yaml_valid(registry, yaml_file, config):
    config.get.return_value = {'test': 'config'}
    registry = ComponentRegistry.from_yaml(config, yaml_file)
    component = registry.get(MockComponent)
    assert isinstance(component, MockComponent)
    assert component.config == {'test': 'config'}

def test_from_yaml_invalid_structure(registry, tmp_path):
    # Missing required 'components' key
    invalid_yaml = {'invalid': 'structure'}
    path = tmp_path / 'invalid.yaml'
    path.write_text(yaml.dump(invalid_yaml))
    
    with pytest.raises(RegistryError) as exc_info:
        ComponentRegistry.from_yaml(Mock(spec=Config), path)
    
    # Optionally verify the error message
    assert "components' key missing" in str(exc_info.value)

def test_from_yaml_missing_required_fields(registry, tmp_path):
    invalid_yaml = {'components': [{'module': 'test'}]}
    path = tmp_path / 'invalid.yaml'
    path.write_text(yaml.dump(invalid_yaml))
    
    with pytest.raises(RegistryError) as exc_info:
        ComponentRegistry.from_yaml(Mock(spec=Config), path)

    # Optionally verify the error message
    assert "Component configuration must include 'module' and 'class'" in str(exc_info.value)

def test_context_manager(registry):
    component_class = MockComponentWithCleanup
    
    with registry as r:
        r.register(component_class, {})
        component = r.get(component_class)
        assert component.initialized
        
    assert not component.initialized

def test_multiple_components(registry):
    class ComponentA(MockComponent): pass
    class ComponentB(MockComponent): pass
    
    registry.register(ComponentA, {'type': 'A'})
    registry.register(ComponentB, {'type': 'B'})
    
    component_a = registry.get(ComponentA)
    component_b = registry.get(ComponentB)
    
    assert component_a.config == {'type': 'A'}
    assert component_b.config == {'type': 'B'}

def test_component_reregistration(registry):
    registry.register(MockComponent, {'version': 1})
    first_instance = registry.get(MockComponent)
    
    registry.unregister(MockComponent)
    registry.register(MockComponent, {'version': 2})
    second_instance = registry.get(MockComponent)
    
    assert first_instance is not second_instance
    assert second_instance.config == {'version': 2}

def test_from_yaml_lazy_loading(registry, yaml_file, config):
    config.get.return_value = {'test': 'config'}
    registry = ComponentRegistry.from_yaml(config, yaml_file, lazy=True)
    
    assert MockComponent not in registry._components
    assert not registry._initialized.get(MockComponent, False)
    
    component = registry.get(MockComponent)
    assert isinstance(component, MockComponent)
    assert registry._initialized[MockComponent]

@pytest.mark.parametrize('component_config', [
    {'module': 'nonexistent.module', 'class': 'Class'},
    {'module': 'tests.test_registry', 'class': 'NonexistentClass'},
])
def test_from_yaml_invalid_imports(registry, tmp_path, component_config):
    yaml_content = {'components': [component_config]}
    path = tmp_path / 'invalid_imports.yaml'
    path.write_text(yaml.dump(yaml_content))
    
    with pytest.raises(RegistryError):
        ComponentRegistry.from_yaml(Mock(spec=Config), path)
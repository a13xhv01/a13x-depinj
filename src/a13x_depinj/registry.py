"""
Component Registry Module

This module provides a singleton registry for managing application components with dependency injection.
Key features:
- Component registration with configuration
- Lazy component instantiation
- Component lifecycle management  
- YAML-based component configuration
- Automatic cleanup via context manager

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

from __future__ import annotations

import importlib
from pathlib import Path
from typing import TypeVar, Type, Dict, Any, Optional, Generic
import yaml

from .config import Config
from .errors import (
    RegistryError,
    ComponentNotFoundError,
    ComponentInitializationError,
    InvalidConfigurationError
)

T = TypeVar('T')

class Singleton(type):
    """Metaclass for implementing the Singleton pattern."""
    _instances: Dict[Type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ComponentRegistry(Generic[T], metaclass=Singleton):
    """
    A singleton registry for managing application components with dependency injection.
    
    This registry allows for:
    - Component registration with configuration
    - Lazy component instantiation
    - Component lifecycle management
    - YAML-based component configuration
    """
    
    def __init__(self):
        self._components: Dict[Type[T], T] = {}
        self._configs: Dict[Type[T], Dict[str, Any]] = {}
        self._initialized: Dict[Type[T], bool] = {}
    
    def register(
        self, 
        component_type: Type[T], 
        config: Optional[Dict[str, Any]] = None,
        lazy: bool = False
    ) -> None:
        """
        Register a component with optional configuration.
        
        Args:
            component_type: The class type of the component
            config: Optional configuration dictionary
            lazy: If True, delay instantiation until first use
            
        Raises:
            ComponentInitializationError: If component initialization fails
        """
        try:
            self._configs[component_type] = config or {}
            if not lazy:
                self._initialize_component(component_type)
            else:
                self._initialized[component_type] = False
        except Exception as e:
            raise ComponentInitializationError(
                f"Failed to register component {component_type.__name__}: {str(e)}"
            ) from e

    def _initialize_component(self, component_type: Type[T]) -> None:
        """
        Initialize a component with its configuration.
        
        Args:
            component_type: The class type of the component to initialize
            
        Raises:
            ComponentInitializationError: If initialization fails
        """
        try:
            instance = component_type(self._configs[component_type])
            self._components[component_type] = instance
            self._initialized[component_type] = True
        except Exception as e:
            raise ComponentInitializationError(
                f"Failed to initialize component {component_type.__name__}: {str(e)}"
            ) from e
    
    def get(self, component_type: Type[T]) -> T:
        """
        Retrieve a component instance.
        
        Args:
            component_type: The class type of the component to retrieve
            
        Returns:
            The component instance
            
        Raises:
            ComponentNotFoundError: If component is not registered
        """
        if component_type not in self._configs:
            raise ComponentNotFoundError(
                f"Component {component_type.__name__} not registered"
            )
            
        if not self._initialized.get(component_type, False):
            self._initialize_component(component_type)
            
        return self._components[component_type]
    
    def unregister(self, component_type: Type[T]) -> None:
        """
        Unregister and cleanup a component.
        
        Args:
            component_type: The class type of the component to unregister
        """
        if hasattr(self._components.get(component_type), 'cleanup'):
            self._components[component_type].cleanup()
            
        self._components.pop(component_type, None)
        self._configs.pop(component_type, None)
        self._initialized.pop(component_type, None)

    @classmethod
    def from_yaml(
        cls, 
        cfg: Config, 
        yaml_path: Path | str,
        lazy: bool = False
    ) -> ComponentRegistry:
        """
        Create a registry from YAML configuration.
        
        Args:
            cfg: Application configuration
            yaml_path: Path to YAML deployment file
            lazy: If True, components are initialized on first use
            
        Returns:
            Configured ComponentRegistry instance
            
        Raises:
            InvalidConfigurationError: If YAML configuration is invalid
            RegistryError: If component initialization fails
        """
        registry = cls()
        yaml_path = Path(yaml_path)
        
        try:
            with open(yaml_path, encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            if not isinstance(config, dict) or 'components' not in config:
                raise InvalidConfigurationError(
                    f"Invalid YAML structure in {yaml_path}. 'components' key missing."
                )
                
            for component_config in config['components']:
                try:
                    if not all(k in component_config for k in ('module', 'class')):
                        raise InvalidConfigurationError(
                            f"Component configuration must include 'module' and 'class'"
                        )
                        
                    module = importlib.import_module(component_config['module'])
                    component_class = getattr(module, component_config['class'])
                    
                    config_path = component_config.get('params', {}).get('path')
                    component_params = cfg.get(config_path) if config_path else None
                    
                    registry.register(
                        component_class,
                        component_params,
                        lazy=lazy
                    )
                    
                except (ImportError, AttributeError) as e:
                    raise InvalidConfigurationError(
                        f"Failed to load component {component_config}: {str(e)}"
                    ) from e
                    
        except Exception as e:
            raise RegistryError(f"Failed to initialize registry: {str(e)}") from e
            
        return registry

    def __enter__(self) -> ComponentRegistry:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cleanup all components on context exit."""
        for component_type in list(self._components.keys()):
            self.unregister(component_type)
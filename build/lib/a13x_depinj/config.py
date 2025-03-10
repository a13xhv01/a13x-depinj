"""
Configuration Management Module

This module provides a thread-safe configuration management system with dot notation access.
It handles loading and validating YAML configuration files from various standard locations,
with support for environment variable overrides.

Key features:
- Singleton configuration instance
- Thread-safe operations
- Dot notation access to nested config values 
- Automatic config file discovery
- Configuration validation
- Deep copy of config values
- Reload capability

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

import os
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional, Union
import yaml

from .errors import ConfigurationError, ConfigDiscoveryError
from .utils import discover_project_root

class Config:
    """Thread-safe configuration management with dot notation access."""
    
    _instance: Optional[Config] = None
    _config: Dict[str, Any] = {}
    _instance_lock = Lock()
    _config_lock = Lock()
    _initialized = False
    
    def __new__(cls) -> Config:
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            with self._config_lock:
                if not self._initialized:
                    self._initialized = True

    @classmethod
    def _validate_config(cls, config: Dict[str, Any]) -> None:
        """
        Validate configuration structure and types.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ConfigurationError: If validation fails
        """
        if not isinstance(config, dict):
            raise ConfigurationError("Configuration must be a dictionary")
            
        # Add your validation rules here
        required_sections = []
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(f"Missing required configuration section: {section}")

    @classmethod
    @lru_cache(maxsize=1)
    def load_config(cls, config_path: Optional[Union[str, Path]] = None) -> 'Config':
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file. If None or file not found,
                        searches in default locations using find_config_file().
        
        Returns:
            Config instance
        
        Raises:
            ConfigurationError: If configuration loading or validation fails
            ConfigDiscoveryError: If configuration file cannot be found
        """
        if not cls._config:
            with cls._config_lock:
                if not cls._config:
                    try:
                        # If config_path is provided, try to resolve it
                        if config_path is not None:
                            path = Path(config_path)
                            # Try to resolve the path (handles both absolute and relative paths)
                            try:
                                resolved_path = path.resolve(strict=True)
                                if resolved_path.is_file():
                                    config_path = resolved_path
                                else:
                                    config_path = find_config_file(path.name)
                            except (OSError, RuntimeError):
                                # Path doesn't exist or can't be resolved
                                config_path = find_config_file(path.name)
                        else:
                            # No path provided, use default config file name
                            config_path = find_config_file()
                        
                        # At this point config_path should be a valid Path
                        cls._config = yaml.safe_load(Path(config_path).read_text(encoding='utf-8'))
                        cls._validate_config(cls._config)
                        
                    except yaml.YAMLError as e:
                        raise ConfigurationError(f"Failed to parse config file: {str(e)}") from e
                    except OSError as e:
                        raise ConfigDiscoveryError(
                            str(config_path),
                            f"Failed to read config file: {str(e)}"
                        ) from e
        return cls()

    @classmethod
    def clear_config(cls):
        """Clear all configuration state including cache"""
        cls._config.clear()
        cls._instance = None
        cls._initialized = False
        cls.load_config.cache_clear()  # Clear the lru_cache

    def get(self, path: Optional[str], default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            path: Dot-separated configuration path
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        if not path:
            return default
            
        try:
            value = self._config
            for key in path.split('.'):
                value = value[key]
            return deepcopy(value)
        except (KeyError, TypeError):
            return default

    def get_value(self, path: str, default: Any = None) -> Any:
        """Alias for get() method for backward compatibility."""
        return self.get(path, default)

    def get_config(self) -> Dict[str, Any]:
        """Get deep copy of entire configuration."""
        return deepcopy(self._config)

    def reload(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """
        Reload configuration from file.
        
        Args:
            config_path: Optional new configuration path
            
        Raises:
            ConfigurationError: If reload fails
        """
        with self._config_lock:
            self._config.clear()
            self.__class__._instance = None
            self.__class__._initialized = False
            self.load_config(config_path)

def find_config_file(filename: str = "config.yaml") -> Path:
    """
    Find configuration file in standard locations.
    
    Args:
        filename: Configuration filename to search for
        
    Returns:
        Path to configuration file
        
    Raises:
        ConfigDiscoveryError: If configuration file not found
    """
    search_paths = []
    
    # Environment variable override
    if config_dir := os.getenv("APP_CONFIG_DIR"):
        search_paths.append(Path(config_dir) / filename)
    
    try:
        project_root = discover_project_root()
        search_paths.extend([
            project_root / filename,
            project_root / "config" / filename,
            project_root / "conf" / filename,
        ])
    except ConfigDiscoveryError as e:
        raise ConfigDiscoveryError("config", str(e)) from e
    
    # Current directory
    search_paths.append(Path.cwd() / filename)
    
    # XDG config directory
    if xdg_config := os.getenv("XDG_CONFIG_HOME"):
        search_paths.append(Path(xdg_config) / filename)
    
    # Search all paths
    for path in search_paths:
        if path.is_file():
            return path
    
    raise ConfigDiscoveryError(
        "config",
        f"Configuration file '{filename}' not found. Searched:\n" +
        "\n".join(f"  - {p}" for p in search_paths)
    )
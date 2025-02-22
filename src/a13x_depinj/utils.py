"""
Configuration discovery utilities for Python projects.

This module provides functionality for:
- Finding project root directories
- Discovering configuration files in standard locations 
- Path normalization and validation
- Python identifier validation

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
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Set

from .errors import ConfigDiscoveryError

PROJECT_MARKERS: Set[str] = {
    '.git',
    'pyproject.toml',
    'setup.py',
    'setup.cfg',
    'src',
    'requirements.txt',
    'poetry.lock',
    'Pipfile'
}

@lru_cache(maxsize=1)
def discover_project_root(start_dir: Optional[Path] = None) -> Path:
    """
    Find the project root directory by looking for common project markers.
    
    Args:
        start_dir: Starting directory for search (default: current working directory)
        
    Returns:
        Path to project root directory
        
    Raises:
        ConfigDiscoveryError: If project root cannot be determined
    """
    current_dir = start_dir or Path.cwd()
    
    try:
        current_dir = current_dir.resolve(strict=True)
    except (OSError, RuntimeError) as e:
        raise ConfigDiscoveryError(str(current_dir), f"Invalid directory path: {str(e)}")
    
    while current_dir != current_dir.parent:
        if any((current_dir / marker).exists() for marker in PROJECT_MARKERS):
            return current_dir
        current_dir = current_dir.parent
        
    raise ConfigDiscoveryError(
        str(current_dir),
        "Unable to determine project root directory"
    )

def get_search_paths(filename: str) -> List[Path]:
    """
    Get standard search paths for configuration files.
    
    Args:
        filename: Name of file to search for
        
    Returns:
        List of paths to search
    """
    search_paths = []
    
    # Environment variable paths
    for env_var in ['APP_CONFIG_DIR', 'XDG_CONFIG_HOME']:
        if config_dir := os.getenv(env_var):
            search_paths.append(Path(config_dir) / filename)
    
    # Project paths
    try:
        project_root = discover_project_root()
        search_paths.extend([
            project_root / filename,
            project_root / "config" / filename,
            project_root / "conf" / filename,
        ])
    except ConfigDiscoveryError:
        pass
    
    # Current directory
    search_paths.append(Path.cwd() / filename)
    
    return search_paths

def normalize_path(path: Path | str) -> Path:
    """
    Normalize path to absolute path with resolved symlinks.
    
    Args:
        path: Path to normalize
        
    Returns:
        Normalized Path object
        
    Raises:
        ConfigDiscoveryError: If path is invalid
    """
    try:
        return Path(path).resolve(strict=True)
    except (OSError, RuntimeError) as e:
        raise ConfigDiscoveryError(str(path), f"Invalid path: {str(e)}")

def is_valid_identifier(name: str) -> bool:
    """Check if string is valid Python identifier."""
    return name.isidentifier() and not name.startswith('_')

def validate_class_name(name: str) -> bool:
    """Check if string is valid Python class name."""
    return (is_valid_identifier(name) and 
            name[0].isupper() if name else False)
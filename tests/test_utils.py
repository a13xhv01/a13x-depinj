"""
Test suite for utility functions in the a13x_depinj package.

Tests functionality for:
- Project root discovery
- Config file search paths
- Path normalization
- Identifier validation
- Class name validation

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
from unittest.mock import patch

from a13x_depinj.utils import (
    discover_project_root,
    get_search_paths,
    normalize_path,
    is_valid_identifier,
    validate_class_name,
    PROJECT_MARKERS
)
from a13x_depinj.errors import ConfigDiscoveryError

@pytest.fixture
def temp_project_structure(tmp_path):
    # Create a temporary project structure
    (tmp_path / "src").mkdir()
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "config").mkdir()
    return tmp_path

def test_discover_project_root(temp_project_structure):
    with patch("pathlib.Path.cwd", return_value=temp_project_structure):
        root = discover_project_root()
        assert root == temp_project_structure

def test_discover_project_root_from_subdirectory(temp_project_structure):
    subdir = temp_project_structure / "src" / "deep" / "nested"
    subdir.mkdir(parents=True)
    
    with patch("pathlib.Path.cwd", return_value=subdir):
        root = discover_project_root()
        assert root == temp_project_structure

def test_discover_project_root_no_markers():
    with patch("pathlib.Path.cwd", return_value=Path("/tmp/no_project")):
        with pytest.raises(ConfigDiscoveryError):
            discover_project_root()

@pytest.mark.parametrize("marker", PROJECT_MARKERS)
def test_discover_project_root_different_markers(tmp_path, marker):
    (tmp_path / marker).touch()
    with patch("pathlib.Path.cwd", return_value=tmp_path):
        root = discover_project_root()
        assert root == tmp_path

def test_get_search_paths():
    filename = "config.yaml"
    env_paths = {
        "APP_CONFIG_DIR": "/app/config",
        "XDG_CONFIG_HOME": "/home/user/.config"
    }
    
    with patch.dict(os.environ, env_paths, clear=True):
        paths = get_search_paths(filename)
        
        assert Path("/app/config/config.yaml") in paths
        assert Path("/home/user/.config/config.yaml") in paths
        assert Path.cwd() / filename in paths

def test_normalize_path_valid(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.touch()
    
    normalized = normalize_path(test_file)
    assert normalized.is_absolute()
    assert normalized.exists()

def test_normalize_path_invalid():
    with pytest.raises(ConfigDiscoveryError):
        normalize_path("/nonexistent/path/file.txt")

def test_normalize_path_symlink(tmp_path):
    real_file = tmp_path / "real.txt"
    real_file.touch()
    symlink = tmp_path / "link.txt"
    symlink.symlink_to(real_file)
    
    normalized = normalize_path(symlink)
    assert normalized.is_absolute()
    assert not normalized.is_symlink()
    assert normalized == real_file.resolve()

@pytest.mark.parametrize("identifier,expected", [
    ("valid_name", True),
    ("ValidName", True),
    ("invalid-name", False),
    ("_private", False),
    ("2invalid", False),
    ("", False),
    ("valid123", True),
])
def test_is_valid_identifier(identifier, expected):
    assert is_valid_identifier(identifier) == expected

@pytest.mark.parametrize("class_name,expected", [
    ("ValidClass", True),
    ("invalid_class", False),
    ("invalidClass", False),
    ("_InvalidClass", False),
    ("2InvalidClass", False),
    ("", False),
    ("ValidClass123", True),
])
def test_validate_class_name(class_name, expected):
    assert validate_class_name(class_name) == expected

def test_discover_project_root_cache(temp_project_structure):
    tmp_path = temp_project_structure
    with patch("pathlib.Path.cwd") as mock_cwd, \
         patch.object(Path, "exists") as mock_exists:
        mock_cwd.return_value = Path(tmp_path)
        
        # Mock exists to return True only for specific project markers
        def mock_exists_impl(path):
            return path.name in {'.git', 'pyproject.toml'}
        mock_exists.side_effect = mock_exists_impl
        
        discover_project_root()
        discover_project_root()
        
        assert mock_cwd.call_count == 1  # Function result was cached

def test_discover_project_root_invalid_path():
    with patch("pathlib.Path.resolve", side_effect=OSError("Invalid path")):
        with pytest.raises(ConfigDiscoveryError):
            discover_project_root()

def test_get_search_paths_empty_env():
    with patch.dict(os.environ, {}, clear=True):
        paths = get_search_paths("config.yaml")
        assert Path.cwd() / "config.yaml" in paths
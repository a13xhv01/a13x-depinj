"""
Custom exception classes for dependency injection framework

This module defines the exception hierarchy used throughout the dependency injection
framework to handle various error conditions related to component registration,
initialization, and configuration.

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

class DepinjError(Exception):
    """Base exception for all dependency injection related errors."""

class RegistryError(DepinjError):
    """Raised when there's a general error in the component registry."""

class ComponentNotFoundError(RegistryError):
    """Raised when attempting to retrieve an unregistered component."""

class ComponentInitializationError(RegistryError):
    """Raised when a component fails to initialize."""

class InvalidConfigurationError(DepinjError):
    """Raised when configuration format or content is invalid."""

class ConfigurationError(DepinjError):
    """Raised when there's an error processing configuration files."""

class ConfigDiscoveryError(ConfigurationError):
    """Raised when configuration file cannot be found."""
    
    def __init__(self, search_path: str, message: str):
        self.search_path = search_path
        super().__init__(message)
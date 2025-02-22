# a13x-depinj Documentation

A lightweight dependency injection framework for Python applications.

## Installation

```bash
pip install a13x-depinj
```

## Core Features

- YAML-based component configuration
- Lazy component initialization
- Automatic dependency management
- Component lifecycle handling
- Thread-safe singleton registry
- Comprehensive error handling

## Quick Start

### Basic Usage

```python
from a13x_depinj import ComponentRegistry, Config

# Define components
class Database:
    def __init__(self, config):
        self.config = config
        
    def connect(self):
        print(f"Connecting to {self.config['host']}")

# Load configuration
config = Config.load_config('config.yaml')

# Initialize registry
with ComponentRegistry.from_yaml(config, 'deployment.yaml') as registry:
    db = registry.get(Database)
    db.connect()
```

### Configuration Files

config.yaml:
```yaml
database:
  host: localhost
  port: 5432
  username: admin
```

deployment.yaml:
```yaml
components:
  - module: myapp.database
    class: Database
    params:
      path: database
```

## API Reference

### ComponentRegistry

Core class for managing component dependencies.

```python
class ComponentRegistry:
    def register(self, component_type: Type[T], config: Optional[Dict] = None, lazy: bool = False) -> None:
        """Register a component with optional configuration."""
        
    def get(self, component_type: Type[T]) -> T:
        """Retrieve a component instance."""
        
    def unregister(self, component_type: Type[T]) -> None:
        """Unregister and cleanup a component."""
        
    @classmethod
    def from_yaml(cls, cfg: Config, yaml_path: Path, lazy: bool = False) -> ComponentRegistry:
        """Create registry from YAML configuration."""
```

### Config

Configuration management with dot notation access.

```python
class Config:
    @classmethod
    def load_config(cls, config_path: Optional[str] = None) -> Config:
        """Load configuration from YAML file."""
        
    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
```

## Component Lifecycle

Components can implement lifecycle methods:

```python
class Component:
    def __init__(self, config: dict):
        self.config = config
        
    def cleanup(self) -> None:
        """Called during unregistration or context exit."""
```

## Error Handling

```python
from a13x_depinj.errors import (
    ComponentNotFoundError,
    ComponentInitializationError,
    InvalidConfigurationError
)

try:
    component = registry.get(MyComponent)
except ComponentNotFoundError:
    print("Component not registered")
```

## Advanced Features

### Lazy Loading

```python
registry = ComponentRegistry.from_yaml(config, 'deployment.yaml', lazy=True)
```

### Event System

```python
class EventListener(Protocol):
    async def on_event(self, event: Event) -> None: ...

class MetricsCollector(EventListener):
    async def on_event(self, event: Event) -> None:
        print(f"Event: {event.type} - {event.data}")
```

### Custom Component Factories

```python
class ComponentFactory:
    @staticmethod
    def create_component(component_type: Type, config: Dict) -> Any:
        return component_type(config)
```

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=a13x_depinj
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](../LICENSE) for details.
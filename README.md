# a13x-depinj

A lightweight, yet powerful dependency injection framework for Python applications.

## Features

- Simple and intuitive API
- YAML-based component configuration
- Lazy component initialization
- Automatic dependency management
- Component lifecycle management
- Type hints support
- Context manager interface

## Installation

```bash
pip install a13x-depinj
```

## Quick Start

1. Define your components:

```python
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    url: str
    port: int

class Database:
    def __init__(self, config: dict):
        self.config = DatabaseConfig(**config)
        
    def connect(self):
        # Implementation
        pass

class UserService:
    def __init__(self, config: dict):
        self.db = ComponentRegistry().get(Database)
```

2. Create a deployment configuration (deployment.yaml):

```yaml
components:
  - module: myapp.database
    class: Database
    params:
      path: database.config
  - module: myapp.services
    class: UserService
    params:
      path: services.user
```

3. Initialize the registry:

```python
from a13x_depinj import ComponentRegistry, Config

# Load application configuration
config = Config.load_config('config.yaml')

# Initialize components
with ComponentRegistry.from_yaml(config, 'deployment.yaml') as registry:
    # Get component instances
    db = registry.get(Database)
    user_service = registry.get(UserService)
    
    # Use components
    db.connect()
```

## Advanced Usage

### Lazy Initialization

Components can be initialized lazily when first accessed:

```python
registry = ComponentRegistry.from_yaml(config, 'deployment.yaml', lazy=True)
```

### Component Lifecycle Management

Components can implement cleanup methods:

```python
class Database:
    def cleanup(self):
        # Cleanup resources
        pass
```

The registry will automatically call cleanup when using the context manager or when unregistering components.

### Type Hints

The registry supports type hints for better IDE integration:

```python
from typing import TypeVar, Type

T = TypeVar('T')
registry = ComponentRegistry[T]()
db: Database = registry.get(Database)
```

## Contributing

Contributions are welcome! Please check our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
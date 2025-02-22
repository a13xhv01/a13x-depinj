from dataclasses import dataclass
from typing import Optional
from a13x_depinj import ComponentRegistry, Config

# Configuration models
@dataclass
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str

@dataclass
class CacheConfig:
    url: str
    port: int
    db: int = 0

# Components
class Database:
    def __init__(self, config: dict):
        self.config = DatabaseConfig(**config)
        self._connected = False
        
    def connect(self) -> None:
        print(f"Connecting to database {self.config.database} at {self.config.host}:{self.config.port}")
        self._connected = True
        
    def disconnect(self) -> None:
        if self._connected:
            print("Disconnecting from database")
            self._connected = False
            
    def cleanup(self) -> None:
        self.disconnect()

class Cache:
    def __init__(self, config: dict):
        self.config = CacheConfig(**config)
        self._connected = False
        
    def connect(self) -> None:
        print(f"Connecting to cache at {self.config.url}:{self.config.port}")
        self._connected = True
        
    def cleanup(self) -> None:
        if self._connected:
            print("Disconnecting from cache")
            self._connected = False

class UserService:
    def __init__(self, config: Optional[dict] = None):
        registry = ComponentRegistry()
        self.db = registry.get(Database)
        self.cache = registry.get(Cache)
        
    def initialize(self) -> None:
        self.db.connect()
        self.cache.connect()
        
    def cleanup(self) -> None:
        self.db.disconnect()

def main():
    # Load configuration
    config = Config.load_config('config.yaml')
    
    # Initialize components using YAML configuration
    with ComponentRegistry.from_yaml(config, 'deployment.yaml') as registry:
        # Get and use components
        user_service = registry.get(UserService)
        user_service.initialize()
        
        # Components will be automatically cleaned up when exiting context

if __name__ == '__main__':
    main()

# Example config.yaml:
"""
database:
  host: localhost
  port: 5432
  username: admin
  password: secret
  database: userdb

cache:
  url: redis://localhost
  port: 6379
  db: 0
"""

# Example deployment.yaml:
"""
components:
  - module: basic_usage
    class: Database
    params:
      path: database
  - module: basic_usage
    class: Cache
    params:
      path: cache
  - module: basic_usage
    class: UserService
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Type
from a13x_depinj import ComponentRegistry, Config

# Event System
class EventType(Enum):
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    ERROR = "error"

@dataclass
class Event:
    type: EventType
    data: Dict[str, Any]

class EventListener(Protocol):
    async def on_event(self, event: Event) -> None: ...

# Component Factory
class ComponentFactory:
    @staticmethod
    def create_component(component_type: Type, config: Dict[str, Any]) -> Any:
        if hasattr(component_type, 'create'):
            return component_type.create(config)
        return component_type(config)

# Base Components
class BaseComponent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._event_listeners: List[EventListener] = []
        
    async def emit_event(self, event: Event) -> None:
        for listener in self._event_listeners:
            await listener.on_event(event)
            
    def add_listener(self, listener: EventListener) -> None:
        self._event_listeners.append(listener)

# Database Components
class DatabasePool:
    @classmethod
    def create(cls, config: Dict[str, Any]) -> 'DatabasePool':
        return cls(config)
        
    def __init__(self, config: Dict[str, Any]):
        self.size = config.get('pool_size', 10)
        print(f"Creating database pool with size {self.size}")
        
    def cleanup(self) -> None:
        print("Cleaning up database pool")

class DatabaseClient(BaseComponent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        registry = ComponentRegistry()
        self.pool = registry.get(DatabasePool)
        
    async def connect(self) -> None:
        await self.emit_event(Event(
            type=EventType.STARTUP,
            data={"component": "DatabaseClient"}
        ))

# Cache Components
class CacheClient(BaseComponent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._connected = False
        
    async def connect(self) -> None:
        self._connected = True
        await self.emit_event(Event(
            type=EventType.STARTUP,
            data={"component": "CacheClient"}
        ))
        
    def cleanup(self) -> None:
        if self._connected:
            print("Disconnecting cache client")
            self._connected = False

# Monitoring
class MetricsCollector(BaseComponent, EventListener):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.events: List[Event] = []
        
    async def on_event(self, event: Event) -> None:
        self.events.append(event)
        print(f"Collected event: {event.type.value} - {event.data}")

# Application Service
class ApplicationService(BaseComponent):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config or {})
        registry = ComponentRegistry()
        self.db = registry.get(DatabaseClient)
        self.cache = registry.get(CacheClient)
        self.metrics = registry.get(MetricsCollector)
        
        # Set up event listeners
        self.db.add_listener(self.metrics)
        self.cache.add_listener(self.metrics)
        
    async def initialize(self) -> None:
        await asyncio.gather(
            self.db.connect(),
            self.cache.connect()
        )

async def main():
    # Load configuration
    config = Config.load_config('config.yaml')
    
    # Create component factory
    factory = ComponentFactory()
    
    # Initialize registry with lazy loading
    registry = ComponentRegistry.from_yaml(config, 'deployment.yaml', lazy=True)
    
    try:
        # Get and initialize application service
        app_service = registry.get(ApplicationService)
        await app_service.initialize()
        
        # Simulate some work
        await asyncio.sleep(1)
        
    finally:
        # Cleanup is handled by context manager
        registry.unregister(ApplicationService)
        registry.unregister(DatabaseClient)
        registry.unregister(CacheClient)
        registry.unregister(MetricsCollector)

if __name__ == '__main__':
    asyncio.run(main())

# Example config.yaml:
"""
database:
  host: localhost
  port: 5432
  pool_size: 5
  username: admin
  password: secret
  database: appdb

cache:
  url: redis://localhost
  port: 6379
  ttl: 3600

metrics:
  enabled: true
  flush_interval: 60
"""

# Example deployment.yaml:
"""
components:
  - module: advanced_usage
    class: DatabasePool
    params:
      path: database
  - module: advanced_usage
    class: DatabaseClient
    params:
      path: database
  - module: advanced_usage
    class: CacheClient
    params:
      path: cache
  - module: advanced_usage
    class: MetricsCollector
    params:
      path: metrics
  - module: advanced_usage
    class: ApplicationService
"""
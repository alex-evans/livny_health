"""
Base repository interface and in-memory implementation.

The repository pattern abstracts data storage, allowing us to swap
implementations (in-memory, SQLite, Postgres) without changing business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """
    Abstract base repository defining the standard CRUD interface.
    All resource repositories implement this interface.
    """

    @abstractmethod
    async def get(self, id: str) -> T | None:
        """Retrieve a single resource by ID."""
        ...

    @abstractmethod
    async def list(self, **filters: Any) -> list[T]:
        """List resources with optional filters."""
        ...

    @abstractmethod
    async def create(self, resource: T) -> T:
        """Create a new resource."""
        ...

    @abstractmethod
    async def update(self, id: str, resource: T) -> T | None:
        """Update an existing resource."""
        ...

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete a resource by ID. Returns True if deleted."""
        ...


class InMemoryRepository(Repository[T]):
    """
    In-memory implementation of the repository interface.
    Used for development and testing.
    """

    def __init__(self):
        self._store: dict[str, T] = {}

    async def get(self, id: str) -> T | None:
        return self._store.get(id)

    async def list(self, **filters: Any) -> list[T]:
        """
        List all resources, optionally filtered.
        Subclasses should override to implement specific filtering logic.
        """
        return list(self._store.values())

    async def create(self, resource: T) -> T:
        # Get ID from resource - assumes resource has an 'id' attribute
        resource_id = getattr(resource, "id", None)
        if not resource_id:
            raise ValueError("Resource must have an 'id' attribute")
        self._store[resource_id] = resource
        return resource

    async def update(self, id: str, resource: T) -> T | None:
        if id not in self._store:
            return None
        self._store[id] = resource
        return resource

    async def delete(self, id: str) -> bool:
        if id in self._store:
            del self._store[id]
            return True
        return False

    def _seed(self, resources: list[T]) -> None:
        """Seed the repository with initial data."""
        for resource in resources:
            resource_id = getattr(resource, "id", None)
            if resource_id:
                self._store[resource_id] = resource


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    short_uuid = uuid.uuid4().hex[:8]
    return f"{prefix}-{short_uuid}" if prefix else short_uuid

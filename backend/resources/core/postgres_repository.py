"""
Base PostgreSQL repository implementation.

Provides async CRUD operations for SQLAlchemy ORM models with
automatic conversion to/from domain models via mappers.
"""

from __future__ import annotations

from typing import Generic, TypeVar, Any, Type

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.repository import Repository
from mappers.base import Mapper

DomainModel = TypeVar("DomainModel")
ORMModel = TypeVar("ORMModel")


class PostgresRepository(Repository[DomainModel], Generic[DomainModel, ORMModel]):
    """
    Base PostgreSQL repository implementing async CRUD operations.

    Subclasses should:
    - Set the orm_class attribute to the ORM model class
    - Set the mapper attribute to the appropriate mapper instance
    - Override _apply_filters() to implement resource-specific filtering
    """

    orm_class: Type[ORMModel]
    mapper: Mapper[DomainModel, ORMModel]

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """
        Initialize with a session factory.

        Args:
            session_factory: Async session factory from db.engine
        """
        self._session_factory = session_factory

    async def get(self, id: str) -> DomainModel | None:
        """Retrieve a single resource by ID."""
        async with self._session_factory() as session:
            result = await session.get(self.orm_class, id)
            if result is None:
                return None
            return self.mapper.to_domain(result)

    async def list(self, **filters: Any) -> list[DomainModel]:
        """List resources with optional filters."""
        async with self._session_factory() as session:
            stmt = select(self.orm_class)
            stmt = self._apply_filters(stmt, **filters)
            result = await session.execute(stmt)
            orm_models = result.scalars().all()
            return [self.mapper.to_domain(orm) for orm in orm_models]

    async def create(self, resource: DomainModel) -> DomainModel:
        """Create a new resource."""
        async with self._session_factory() as session:
            orm_model = self.mapper.to_orm(resource)
            session.add(orm_model)
            await session.commit()
            await session.refresh(orm_model)
            return self.mapper.to_domain(orm_model)

    async def update(self, id: str, resource: DomainModel) -> DomainModel | None:
        """Update an existing resource."""
        async with self._session_factory() as session:
            existing = await session.get(self.orm_class, id)
            if existing is None:
                return None

            # Convert domain to ORM and update fields
            orm_model = self.mapper.to_orm(resource)

            # Copy all columns from new ORM model to existing
            for column in self.orm_class.__table__.columns:
                if column.name != "id":  # Don't update primary key
                    setattr(existing, column.name, getattr(orm_model, column.name))

            await session.commit()
            await session.refresh(existing)
            return self.mapper.to_domain(existing)

    async def delete(self, id: str) -> bool:
        """Delete a resource by ID. Returns True if deleted."""
        async with self._session_factory() as session:
            existing = await session.get(self.orm_class, id)
            if existing is None:
                return False

            await session.delete(existing)
            await session.commit()
            return True

    def _apply_filters(self, stmt, **filters: Any):
        """
        Apply filters to a select statement.

        Subclasses should override this to implement resource-specific filtering.
        By default, filters are ignored.

        Args:
            stmt: SQLAlchemy select statement
            **filters: Filter key-value pairs

        Returns:
            Modified select statement with filters applied
        """
        return stmt

    async def _seed(self, resources: list[DomainModel]) -> None:
        """Seed the repository with initial data."""
        async with self._session_factory() as session:
            for resource in resources:
                orm_model = self.mapper.to_orm(resource)
                # Use merge to handle existing records
                await session.merge(orm_model)
            await session.commit()

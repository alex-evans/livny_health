"""
Base mapper interface for domain <-> ORM conversion.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

DomainModel = TypeVar("DomainModel")
ORMModel = TypeVar("ORMModel")


class Mapper(ABC, Generic[DomainModel, ORMModel]):
    """
    Abstract base class for mappers that convert between domain and ORM models.

    Subclasses implement the specific conversion logic for each resource type.
    """

    @abstractmethod
    def to_orm(self, domain: DomainModel) -> ORMModel:
        """
        Convert a domain model instance to an ORM model instance.

        Args:
            domain: The domain model to convert

        Returns:
            The corresponding ORM model
        """
        ...

    @abstractmethod
    def to_domain(self, orm: ORMModel) -> DomainModel:
        """
        Convert an ORM model instance to a domain model instance.

        Args:
            orm: The ORM model to convert

        Returns:
            The corresponding domain model
        """
        ...

    def to_orm_list(self, domains: list[DomainModel]) -> list[ORMModel]:
        """Convert a list of domain models to ORM models."""
        return [self.to_orm(d) for d in domains]

    def to_domain_list(self, orms: list[ORMModel]) -> list[DomainModel]:
        """Convert a list of ORM models to domain models."""
        return [self.to_domain(o) for o in orms]

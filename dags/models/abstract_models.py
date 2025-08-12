from abc import ABC, abstractmethod
from pydantic import BaseModel


class SyncConvention(BaseModel, ABC):
    """
    Base convention which has common attributes for econvention and oscar
    """


class ConventionFactory(ABC):
    """
    Base abstract factory for building or converting convention models.
    """

    @classmethod
    @abstractmethod
    def from_api_payload(cls, data: list[dict]) -> list[dict]:
        """Create a convention instance from a raw API payload."""

    @classmethod
    @abstractmethod
    def convert_from(cls, data: list[dict]) -> str:
        """Convert data to serialize into a JSON formatted string."""

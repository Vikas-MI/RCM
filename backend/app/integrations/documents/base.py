from abc import ABC, abstractmethod
from typing import Any


class DocumentIntelligenceProvider(ABC):
    """ELI5: A robot that reads a scanned paper and types the important fields."""

    @abstractmethod
    def extract(self, *, doc_type: str, filename: str, hint: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError

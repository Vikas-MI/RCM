from abc import ABC, abstractmethod
from typing import Any


class EligibilityProvider(ABC):
    @abstractmethod
    def verify(self, request: dict[str, Any]) -> dict[str, Any]:
        """Return a deterministic eligibility response for the request."""
        raise NotImplementedError

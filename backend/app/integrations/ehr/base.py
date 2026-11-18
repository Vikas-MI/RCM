"""EHR adapter interface — swap HAPI / Epic / Oracle later without rewriting the app."""

from abc import ABC, abstractmethod
from typing import Any


class EHRAdapter(ABC):
    @abstractmethod
    def get_capability_statement(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def search_patients(self, **params: Any) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_patient(self, external_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def search_encounters(self, **params: Any) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def search_coverage(self, **params: Any) -> dict[str, Any]:
        raise NotImplementedError

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from anz_fs_poc.models import Citation


class ProviderUnavailable(RuntimeError):
    """Raised when the model endpoint cannot serve a request (triggers degraded mode)."""


@dataclass(frozen=True)
class ModelOutput:
    text: str
    model_id: str


class ModelProvider(ABC):
    @abstractmethod
    def generate(
        self,
        *,
        query: str,
        citations: list[Citation],
        system_notes: list[str],
        system_prompt: str,
    ) -> ModelOutput:
        raise NotImplementedError

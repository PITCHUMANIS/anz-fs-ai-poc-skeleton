from __future__ import annotations

from anz_fs_poc.config import Settings
from anz_fs_poc.providers.base import ModelProvider
from anz_fs_poc.providers.mock import MockProvider


def get_provider(settings: Settings) -> ModelProvider:
    if settings.provider == "mock":
        return MockProvider(model_id=settings.model_id, unavailable=settings.force_degraded)
    raise ValueError(
        f"Provider '{settings.provider}' is not wired in this scaffold. "
        "Use POC_PROVIDER=mock, or implement a regional provider module."
    )

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
CORPUS_DIR = DATA_DIR / "corpus"
GOLDEN_SET_PATH = DATA_DIR / "golden_set" / "cases.json"


def _load_dotenv(path: Path) -> None:
    """Tiny .env loader — avoids an external dependency for the scaffold."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv(REPO_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    provider: str = os.getenv("POC_PROVIDER", "mock")
    model_id: str = os.getenv("POC_MODEL_ID", "mock-fs-assist-v1")
    region: str = os.getenv("POC_REGION", "australia-east")
    min_retrieval_score: float = float(os.getenv("POC_MIN_RETRIEVAL_SCORE", "0.15"))
    force_degraded: bool = os.getenv("POC_FORCE_DEGRADED", "false").strip().lower() in {"1", "true", "yes"}
    audit_dir: Path = Path(os.getenv("POC_AUDIT_DIR", str(REPO_ROOT / ".audit")))
    corpus_dir: Path = CORPUS_DIR
    golden_set_path: Path = GOLDEN_SET_PATH


def get_settings() -> Settings:
    return Settings()

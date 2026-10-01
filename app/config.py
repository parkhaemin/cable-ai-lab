"""One place for paths and local/live configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def mode() -> str:
    value = os.getenv("CABLE_MODE", "demo").lower().strip()
    if value not in {"demo", "live"}:
        raise ValueError("CABLE_MODE must be demo or live")
    return value


def live_settings() -> tuple[str, str, str, str]:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise ValueError("live 모드에는 .env의 OPENAI_API_KEY가 필요합니다.")
    return (
        key,
        os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        os.getenv("DATABASE_URL", "postgresql://cable:cable_local@localhost:5433/cableai_lab"),
    )


def minimum_score(run_mode: str) -> float:
    name = "DEMO_MIN_SCORE" if run_mode == "demo" else "LIVE_MIN_SCORE"
    value = float(os.getenv(name, "0.05" if run_mode == "demo" else "0.65"))
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return value

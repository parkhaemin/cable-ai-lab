"""Read the small, openly labeled sample data."""
import json
from .config import ROOT


def load_documents() -> list[dict]:
    return json.loads((ROOT / "data" / "knowledge.json").read_text(encoding="utf-8"))


def load_products() -> list[dict]:
    return json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))


def product_by_id(product_id: str) -> dict | None:
    return next((item for item in load_products() if item["id"] == product_id), None)

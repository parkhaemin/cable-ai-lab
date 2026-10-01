"""Week 2 live mode: create an isolated table and upsert embedded documents."""
from app.db import ingest

if __name__ == "__main__":
    print(f"저장한 문서: {ingest()}개")

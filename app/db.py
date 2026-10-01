"""Live mode only: OpenAI embeddings + isolated PostgreSQL pgvector table."""
from .config import live_settings
from .data import load_documents

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS cable_lab_documents (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL
)
"""


def _connect():
    import psycopg
    from pgvector.psycopg import register_vector
    *_, database_url = live_settings()
    conn = psycopg.connect(database_url)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def ingest() -> int:
    from openai import OpenAI
    from pgvector import Vector
    key, _, embedding_model, _ = live_settings()
    if embedding_model != "text-embedding-3-small":
        raise ValueError("현재 VECTOR(1536) 스키마는 text-embedding-3-small 기본 차원 전용입니다.")
    docs = load_documents()
    client = OpenAI(api_key=key)
    texts = [doc["title"] + "\n" + doc["content"] for doc in docs]
    vectors = client.embeddings.create(model=embedding_model, input=texts).data
    with _connect() as conn:
        conn.execute(CREATE_TABLE)
        for doc, item in zip(docs, vectors):
            conn.execute(
                """INSERT INTO cable_lab_documents (id, source, title, content, embedding)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (id) DO UPDATE SET source=EXCLUDED.source,
                     title=EXCLUDED.title, content=EXCLUDED.content,
                     embedding=EXCLUDED.embedding""",
                (doc["id"], doc["source"], doc["title"], doc["content"], Vector(item.embedding)),
            )
    return len(docs)


def search_live(query: str, top_k: int = 3) -> list[dict]:
    from openai import OpenAI
    from pgvector import Vector
    key, _, embedding_model, _ = live_settings()
    client = OpenAI(api_key=key)
    vector = Vector(client.embeddings.create(model=embedding_model, input=query).data[0].embedding)
    with _connect() as conn:
        rows = conn.execute(
            """SELECT id, source, title, content, embedding <=> %s AS distance
               FROM cable_lab_documents
               ORDER BY embedding <=> %s LIMIT %s""",
            (vector, vector, top_k),
        ).fetchall()
    return [
        {"id": r[0], "source": r[1], "title": r[2], "content": r[3],
         "score": round(max(0.0, 1.0 - float(r[4])), 4)}
        for r in rows
    ]

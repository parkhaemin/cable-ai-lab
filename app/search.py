"""Retrieval: local character TF-IDF for demo; pgvector for live."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .data import load_documents


def search_demo(query: str, top_k: int = 3) -> list[dict]:
    documents = load_documents()
    corpus = [doc["title"] + " " + doc["content"] for doc in documents]
    matrix = TfidfVectorizer(analyzer="char", ngram_range=(2, 4)).fit_transform(
        corpus + [query]
    )
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    ranked = sorted(range(len(documents)), key=lambda i: -scores[i])[:top_k]
    return [{**documents[i], "score": round(float(scores[i]), 4)} for i in ranked]


def search(query: str, top_k: int = 3, run_mode: str = "demo") -> list[dict]:
    if run_mode == "demo":
        return search_demo(query, top_k)
    from .db import search_live
    return search_live(query, top_k)

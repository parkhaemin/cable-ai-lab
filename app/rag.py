"""Retrieval-augmented answers with visible evidence."""
from .config import live_settings, minimum_score
from .search import search

UNKNOWN = "제공된 자료에서 확인할 수 없습니다."


def answer_question(question: str, run_mode: str = "demo", top_k: int = 3) -> dict:
    ranked = search(question, top_k, run_mode)
    hits = [hit for hit in ranked if hit["score"] >= minimum_score(run_mode)]
    if not hits:
        return {"answer": UNKNOWN, "sources": [], "retrieval": ranked,
                "mode": run_mode, "generated": False}
    if run_mode == "demo":
        first = hits[0]
        answer = f'{first["content"]} [{first["id"]}]'
        generated = False
    else:
        from openai import OpenAI
        key, model, _, _ = live_settings()
        context = "\n".join(
            f'[{h["id"]}] {h["title"]}: {h["content"]}' for h in hits
        )
        response = OpenAI(api_key=key).responses.create(
            model=model,
            instructions=("제공된 자료만으로 한국어로 답하세요. 근거 id를 [id]로 표시하세요. "
                          "자료에 답이 없으면 '제공된 자료에서 확인할 수 없습니다.'라고 답하세요."),
            input=f"자료:\n{context}\n\n질문: {question}",
            max_output_tokens=350,
        )
        answer = response.output_text.strip() or UNKNOWN
        generated = True
    return {"answer": answer, "sources": hits, "retrieval": ranked,
            "mode": run_mode, "generated": generated}

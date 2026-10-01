"""Week 1 and 4: evaluate retrieval separately from answer generation."""
import csv
from app.config import ROOT, mode
from app.rag import answer_question


def main():
    path = ROOT / "data" / "evaluation.csv"
    with path.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    retrieval_correct = 0
    answer_correct = 0
    for row in rows:
        result = answer_question(row["question"], mode())
        top = result["retrieval"][0]["id"] if result["retrieval"] else ""
        retrieval_ok = (top == row["expected_top_id"]) if row["expected_top_id"] else (not result["sources"])
        answer_ok = bool(result["sources"]) == (row["expect_answer"] == "1")
        retrieval_correct += retrieval_ok
        answer_correct += answer_ok
        print(f'검색 {"OK" if retrieval_ok else "CHECK"} / 답변 {"OK" if answer_ok else "CHECK"}'
              f' | {row["question"]} | top={top} | answer={result["answer"]}')
    print(f"검색 기대 출처: {retrieval_correct}/{len(rows)}")
    print(f"근거 유무 판단: {answer_correct}/{len(rows)}")
    print("이 두 수치는 답변의 사실성·문장 품질을 보증하지 않습니다. 문서와 비교해 수동 검토하세요.")


if __name__ == "__main__":
    main()

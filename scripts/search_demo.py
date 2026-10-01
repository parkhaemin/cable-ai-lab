"""Week 1: inspect retrieval scores before reading generated answers."""
from app.search import search_demo
from app.rag import answer_question


def main():
    question = "상품 문의는 어디에서 하나요?"
    for hit in search_demo(question):
        print(f'{hit["id"]}: similarity={hit["score"]:.4f} | {hit["content"]}')
    print("답변:", answer_question(question)["answer"])


if __name__ == "__main__":
    main()

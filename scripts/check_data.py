"""Week 1: inspect what the service is allowed to answer from."""
from app.data import load_documents, load_products


def main():
    docs, products = load_documents(), load_products()
    print(f"문서 {len(docs)}개, 예시 상품 {len(products)}개")
    for doc in docs:
        print(f'{doc["id"]:17} | {doc["title"]} | {doc["source"]}')


if __name__ == "__main__":
    main()

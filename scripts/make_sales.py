"""Generate 80 reproducible fictional sales rows for the ML lesson."""
import csv
import random
from app.config import ROOT
from app.data import load_products


def main():
    rng = random.Random(42)
    products = load_products()
    path = ROOT / "data" / "sales_sample.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "product_id", "price", "discount_pct", "ad_spend", "weekend", "quantity"
        ])
        writer.writeheader()
        for index in range(80):
            product = products[index % len(products)]
            discount = rng.choice([0, 10, 20])
            ad_spend = rng.choice([0, 10000, 20000])
            weekend = index % 2
            quantity = max(1, round(
                25 - product["price"] / 10000 * 1.8
                + discount * 0.45 + ad_spend / 8000
                + weekend * 3 + rng.gauss(0, 2)
            ))
            writer.writerow(dict(product_id=product["id"], price=product["price"],
                                 discount_pct=discount, ad_spend=ad_spend,
                                 weekend=weekend, quantity=quantity))
    print(f"가상 판매 데이터 80행 저장: {path}")


if __name__ == "__main__":
    main()

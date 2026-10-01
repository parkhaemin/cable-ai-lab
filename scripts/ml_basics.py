"""A separate supervised ML lesson; it is not the RAG search algorithm."""
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from app.config import ROOT

FEATURES = ["price", "discount_pct", "ad_spend", "weekend"]
TARGET = "quantity"


def main():
    path = ROOT / "data" / "sales_sample.csv"
    if not path.exists():
        raise FileNotFoundError("먼저 python -m scripts.make_sales 를 실행하세요.")
    df = pd.read_csv(path)
    x_train, x_test, y_train, y_test = train_test_split(
        df[FEATURES], df[TARGET], test_size=0.25, random_state=42
    )
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(x_train, y_train)
    predicted = model.predict(x_test)
    model_mae = mean_absolute_error(y_test, predicted)
    baseline_mae = mean_absolute_error(y_test, [y_train.mean()] * len(y_test))
    sample = pd.DataFrame([{"price":39000,"discount_pct":10,
                            "ad_spend":10000,"weekend":1}])
    print(f"학습 {len(x_train)}행 / 평가 {len(x_test)}행")
    print(f"기준선 MAE: {baseline_mae:.2f}개")
    print(f"모델 MAE: {model_mae:.2f}개")
    print(f"예시 예측: {model.predict(sample)[0]:.1f}개")
    print("가상 데이터만 사용합니다. 실제 판매 예측 성능으로 해석하면 안 됩니다.")


if __name__ == "__main__":
    main()

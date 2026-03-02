from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
ARTIFACTS_DIR = PROJECT_ROOT / "ml" / "artifacts"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
DATASET_PATH = PROJECT_ROOT / "ml" / "dataset" / "engineered_materials.csv"


def evaluate_regression(name: str, y_true, y_pred) -> dict[str, float]:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    return {"model": name, "rmse": rmse, "mae": mae, "r2": r2}


def main() -> None:
    cost_model = joblib.load(MODELS_DIR / "cost_model.pkl")
    co2_model = joblib.load(MODELS_DIR / "co2_model.pkl")

    X_test = joblib.load(ARTIFACTS_DIR / "X_test.pkl")
    y_cost_test = joblib.load(ARTIFACTS_DIR / "y_cost_test.pkl")
    y_co2_test = joblib.load(ARTIFACTS_DIR / "y_co2_test.pkl")

    cost_pred = cost_model.predict(X_test)
    co2_pred = co2_model.predict(X_test)

    metrics = [
        evaluate_regression("cost_model", y_cost_test, cost_pred),
        evaluate_regression("co2_model", y_co2_test, co2_pred),
    ]
    metrics_df = pd.DataFrame(metrics)

    dataset = pd.read_csv(DATASET_PATH)
    dataset["sustainability_proxy_score"] = (
        0.4 * dataset["biodegradability_score"]
        + 0.3 * dataset["recyclability_percentage"]
        - 0.2 * dataset["co2_emission_score"]
        - 0.1 * dataset["cost_per_unit"]
    )
    top_materials = dataset.sort_values("sustainability_proxy_score", ascending=False).head(10)

    print("=== MODEL METRICS ===")
    print(metrics_df.to_string(index=False))
    print("\n=== TOP 10 MATERIALS BY SUSTAINABILITY PROXY SCORE ===")
    print(
        top_materials[
            ["material_name", "material_type", "cost_per_unit", "co2_emission_score", "sustainability_proxy_score"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()

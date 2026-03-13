from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset" / "materials.csv"
MIN_ROWS = 600
MIN_PER_TYPE = 15


def fail(message: str) -> None:
    raise SystemExit(f"[FAILED] {message}")


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    if len(df) < MIN_ROWS:
        fail(f"Row count {len(df)} is below minimum required {MIN_ROWS}")

    if df.isnull().any().any():
        null_cols = df.columns[df.isnull().any()].tolist()
        fail(f"Null values found in columns: {null_cols}")

    duplicate_ratio = df.duplicated().mean()
    if duplicate_ratio > 0.02:
        fail(f"Duplicate ratio too high: {duplicate_ratio:.2%}")

    constraints = {
        "strength_rating": (1.0, 10.0),
        "weight_capacity": (5.0, 120.0),
        "biodegradability_score": (1.0, 10.0),
        "recyclability_percentage": (0.0, 100.0),
        "co2_emission_score": (1.0, 15.0),
        "cost_per_unit": (2.0, 80.0),
    }

    for col, (low, high) in constraints.items():
        out_of_range = (~df[col].between(low, high)).sum()
        if out_of_range > 0:
            fail(f"{col}: {out_of_range} rows out of range [{low}, {high}]")

    by_type = df["material_type"].value_counts()
    low_types = by_type[by_type < MIN_PER_TYPE]
    if not low_types.empty:
        fail(f"Insufficient rows for types: {low_types.to_dict()}")

    # Directionality checks for business realism.
    corr_cost_strength = df["cost_per_unit"].corr(df["strength_rating"])
    corr_co2_recyclability = df["co2_emission_score"].corr(df["recyclability_percentage"])

    if corr_cost_strength is None or corr_cost_strength < 0.15:
        fail(f"Unexpected low correlation cost vs strength: {corr_cost_strength}")

    if corr_co2_recyclability is None or corr_co2_recyclability > -0.10:
        fail(f"Unexpected weak negative correlation co2 vs recyclability: {corr_co2_recyclability}")

    print("[PASSED] Data quality gate")
    print(f"Rows: {len(df)}")
    print("Material type distribution:")
    print(by_type.to_string())
    print(f"Corr(cost, strength): {corr_cost_strength:.3f}")
    print(f"Corr(co2, recyclability): {corr_co2_recyclability:.3f}")


if __name__ == "__main__":
    main()

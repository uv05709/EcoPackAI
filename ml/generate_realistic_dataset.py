from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"
BASE_DATA_PATH = DATASET_DIR / "real_materials_base.csv"
MATERIALS_PATH = DATASET_DIR / "materials.csv"
CLEANED_PATH = DATASET_DIR / "cleaned_materials.csv"
ENGINEERED_PATH = DATASET_DIR / "engineered_materials.csv"

TARGET_ROWS = 720
RANDOM_SEED = 42

NUMERIC_COLUMNS = [
    "strength_rating",
    "weight_capacity",
    "biodegradability_score",
    "recyclability_percentage",
    "co2_emission_score",
    "cost_per_unit",
]

MATERIAL_TYPE_WEIGHTS = {
    "Paper": 0.16,
    "Pulp": 0.07,
    "Natural Fiber": 0.14,
    "Bioplastic": 0.10,
    "Plastic": 0.21,
    "Glass": 0.09,
    "Metal": 0.10,
    "Wood": 0.08,
    "Biopolymer": 0.05,
}

MATERIAL_TYPE_FACTORS = {
    "Paper": {"co2": 0.90, "cost": 0.95},
    "Pulp": {"co2": 0.82, "cost": 1.00},
    "Natural Fiber": {"co2": 0.88, "cost": 1.05},
    "Bioplastic": {"co2": 1.10, "cost": 1.12},
    "Plastic": {"co2": 1.18, "cost": 1.08},
    "Glass": {"co2": 1.26, "cost": 1.10},
    "Metal": {"co2": 1.22, "cost": 1.16},
    "Wood": {"co2": 0.98, "cost": 1.14},
    "Biopolymer": {"co2": 0.86, "cost": 1.10},
}

REAL_DATASET_PATH = DATASET_DIR / "real_production_materials.csv"


def clamp(value: float, lower: float, upper: float) -> float:
    return float(np.clip(value, lower, upper))


def _safe_weights(base_df: pd.DataFrame) -> dict[str, float]:
    present_types = set(base_df["material_type"].unique())
    filtered = {k: v for k, v in MATERIAL_TYPE_WEIGHTS.items() if k in present_types}

    if not filtered:
        counts = base_df["material_type"].value_counts(normalize=True).to_dict()
        return {str(k): float(v) for k, v in counts.items()}

    total = sum(filtered.values())
    return {k: v / total for k, v in filtered.items()}


def _build_limits(base_df: pd.DataFrame) -> dict[str, tuple[float, float]]:
    limits: dict[str, tuple[float, float]] = {}
    for col in NUMERIC_COLUMNS:
        col_min = float(base_df[col].min())
        col_max = float(base_df[col].max())
        limits[col] = (col_min * 0.80, col_max * 1.25)

    # Strict business-safe caps
    limits["strength_rating"] = (1.0, 10.0)
    limits["biodegradability_score"] = (1.0, 10.0)
    limits["recyclability_percentage"] = (5.0, 100.0)
    limits["weight_capacity"] = (5.0, 120.0)
    limits["co2_emission_score"] = (1.0, 15.0)
    limits["cost_per_unit"] = (2.0, 80.0)
    return limits


def build_realistic_dataset(base_df: pd.DataFrame, target_rows: int, random_seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(random_seed)
    limits = _build_limits(base_df)
    type_weights = _safe_weights(base_df)

    by_type = {t: frame.copy() for t, frame in base_df.groupby("material_type")}
    material_types = np.array(list(type_weights.keys()))
    probabilities = np.array([type_weights[t] for t in material_types], dtype=float)

    records: list[pd.Series] = []

    for _ in range(target_rows):
        selected_type = str(rng.choice(material_types, p=probabilities))
        template_row = by_type[selected_type].sample(n=1, random_state=int(rng.integers(1, 2_000_000))).iloc[0].copy()

        factors = MATERIAL_TYPE_FACTORS.get(selected_type, {"co2": 1.0, "cost": 1.0})
        supplier_variability = float(rng.normal(0.0, 1.0))
        logistics_variability = float(rng.normal(0.0, 1.0))
        process_variability = float(rng.normal(0.0, 1.0))

        base_strength = float(template_row["strength_rating"])
        base_weight = float(template_row["weight_capacity"])
        base_bio = float(template_row["biodegradability_score"])
        base_recy = float(template_row["recyclability_percentage"])
        base_co2 = float(template_row["co2_emission_score"])
        base_cost = float(template_row["cost_per_unit"])

        strength = clamp(round(base_strength + rng.normal(0, 0.55)), *limits["strength_rating"])

        biodegradability = clamp(
            round(base_bio + rng.normal(0, 0.45)),
            *limits["biodegradability_score"],
        )

        weight_capacity = clamp(
            base_weight + rng.normal(0, max(1.3, base_weight * 0.07)) + 1.4 * (strength - base_strength),
            *limits["weight_capacity"],
        )

        recyclability = clamp(
            base_recy + rng.normal(0, 3.2) + 0.8 * (biodegradability - base_bio),
            *limits["recyclability_percentage"],
        )

        # Keep recyclable values sensible for low-recyclable categories.
        if selected_type in {"Glass", "Wood"}:
            recyclability = clamp(recyclability, 20.0, 75.0)
        if selected_type == "Plastic":
            recyclability = clamp(recyclability, 35.0, 95.0)

        co2_emission = (
            base_co2 * factors["co2"]
            + rng.normal(0, 0.78)
            + 0.04 * (strength - base_strength)
            + 0.012 * (weight_capacity - base_weight)
            - 0.007 * (recyclability - base_recy)
            - 0.02 * (biodegradability - base_bio)
            + 0.18 * logistics_variability
            + 0.35 * process_variability
        )
        co2_emission = clamp(co2_emission, *limits["co2_emission_score"])

        cost_per_unit = (
            base_cost * factors["cost"]
            + rng.normal(0, 2.10)
            + 0.42 * (strength - base_strength)
            + 0.022 * (weight_capacity - base_weight)
            + 0.33 * (co2_emission - base_co2)
            + 0.85 * supplier_variability
            + 0.35 * logistics_variability
        )
        cost_per_unit = clamp(cost_per_unit, *limits["cost_per_unit"])

        template_row["strength_rating"] = round(strength, 2)
        template_row["weight_capacity"] = round(weight_capacity, 2)
        template_row["biodegradability_score"] = round(biodegradability, 2)
        template_row["recyclability_percentage"] = round(recyclability, 2)
        template_row["co2_emission_score"] = round(co2_emission, 2)
        template_row["cost_per_unit"] = round(cost_per_unit, 2)

        records.append(template_row)

    out = pd.DataFrame(records)

    # Remove overly duplicated rows for realism.
    out = out.drop_duplicates(subset=["material_name", "material_type", *NUMERIC_COLUMNS]).reset_index(drop=True)
    if len(out) < target_rows:
        # Top-up with deterministic resampling if de-dup reduced count.
        needed = target_rows - len(out)
        extra = out.sample(n=needed, replace=True, random_state=random_seed + 17).copy()
        jitter = np.random.default_rng(random_seed + 100)
        extra["cost_per_unit"] = (extra["cost_per_unit"] + jitter.normal(0, 0.25, size=needed)).clip(2.0, 80.0).round(2)
        extra["co2_emission_score"] = (extra["co2_emission_score"] + jitter.normal(0, 0.09, size=needed)).clip(1.0, 15.0).round(2)
        out = pd.concat([out, extra], ignore_index=True)

    return out.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)


def create_cleaned_and_engineered(df_materials: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cleaned = df_materials.copy()
    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    cleaned = cleaned.fillna(cleaned.mean(numeric_only=True))

    engineered = cleaned.copy()
    engineered["co2_impact_index"] = (
        engineered["co2_emission_score"] * 10 / engineered["recyclability_percentage"].replace(0, np.nan)
    )
    engineered["cost_efficiency_index"] = engineered["strength_rating"] / engineered["cost_per_unit"].replace(0, np.nan)
    engineered["material_suitability_score"] = (
        0.4 * engineered["strength_rating"]
        + 0.3 * engineered["biodegradability_score"]
        + 0.2 * engineered["recyclability_percentage"]
        - 0.1 * engineered["co2_emission_score"]
    )
    engineered = engineered.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    for col in ["co2_impact_index", "cost_efficiency_index", "material_suitability_score"]:
        engineered[col] = engineered[col].round(4)

    return cleaned, engineered


def main() -> None:
    base_df = pd.read_csv(BASE_DATA_PATH)
    generated = build_realistic_dataset(base_df, TARGET_ROWS, RANDOM_SEED)
    cleaned, engineered = create_cleaned_and_engineered(generated)

    generated.to_csv(MATERIALS_PATH, index=False)
    generated.to_csv(REAL_DATASET_PATH, index=False)
    cleaned.to_csv(CLEANED_PATH, index=False)
    engineered.to_csv(ENGINEERED_PATH, index=False)

    print(f"Base rows: {len(base_df)}")
    print(f"Generated rows: {len(generated)}")
    print(f"Saved: {MATERIALS_PATH}")
    print(f"Saved: {REAL_DATASET_PATH}")
    print(f"Saved: {CLEANED_PATH}")
    print(f"Saved: {ENGINEERED_PATH}")


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from flask import Flask, jsonify, request
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

FEATURE_COLUMNS = [
    "strength_rating",
    "weight_capacity",
    "biodegradability_score",
    "recyclability_percentage",
    "material_type_encoded",
    "cost_efficiency_index",
    "co2_impact_index",
    "material_suitability_score",
]

REQUIRED_INPUT_FIELDS = [
    "strength_rating",
    "weight_capacity",
    "biodegradability_score",
    "recyclability_percentage",
    "material_type",
    "cost_efficiency_index",
    "co2_impact_index",
    "material_suitability_score",
]


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def _find_existing_path(candidates: list[Path], label: str) -> Path:
    for candidate in candidates:
        if candidate.exists() and candidate.stat().st_size > 0:
            return candidate
    checked = "\n".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Could not find a valid {label}. Checked:\n{checked}")


def _load_resources() -> dict[str, Any]:
    model_candidates = [BASE_DIR / "models", PROJECT_ROOT / "ml" / "models"]

    cost_model_path = _find_existing_path(
        [path / "cost_model.pkl" for path in model_candidates],
        "cost model",
    )
    co2_model_path = _find_existing_path(
        [path / "co2_model.pkl" for path in model_candidates],
        "CO2 model",
    )
    scaler_path = _find_existing_path(
        [path / "scaler.pkl" for path in model_candidates],
        "scaler",
    )

    dataset_path = _find_existing_path(
        [
            BASE_DIR / "dataset" / "engineered_materials.csv",
            PROJECT_ROOT / "ml" / "dataset" / "engineered_materials.csv",
        ],
        "engineered dataset",
    )

    dataset = pd.read_csv(dataset_path)
    if dataset.empty:
        raise ValueError(f"Dataset is empty: {dataset_path}")

    if "material_type" not in dataset.columns:
        raise ValueError("Dataset is missing required column: material_type")

    encoder = LabelEncoder()
    dataset["material_type_encoded"] = encoder.fit_transform(dataset["material_type"].astype(str))

    for column in FEATURE_COLUMNS:
        if column not in dataset.columns:
            raise ValueError(f"Dataset is missing feature column: {column}")

    return {
        "cost_model": joblib.load(cost_model_path),
        "co2_model": joblib.load(co2_model_path),
        "scaler": joblib.load(scaler_path),
        "dataset": dataset,
        "encoder": encoder,
        "paths": {
            "cost_model": str(cost_model_path),
            "co2_model": str(co2_model_path),
            "scaler": str(scaler_path),
            "dataset": str(dataset_path),
        },
    }


def _validate_and_prepare_materials(materials: list[dict[str, Any]], encoder: LabelEncoder) -> pd.DataFrame:
    if not materials:
        raise ValueError("materials must be a non-empty list")

    frame = pd.DataFrame(materials)

    missing_columns = [field for field in REQUIRED_INPUT_FIELDS if field not in frame.columns]
    if missing_columns:
        raise ValueError(f"Missing required fields: {', '.join(missing_columns)}")

    for numeric_col in REQUIRED_INPUT_FIELDS:
        if numeric_col == "material_type":
            continue
        frame[numeric_col] = pd.to_numeric(frame[numeric_col], errors="coerce")

    if frame.drop(columns=["material_type"]).isnull().any().any():
        raise ValueError("One or more numeric fields have invalid values")

    incoming_types = frame["material_type"].astype(str)
    unknown_types = sorted(set(incoming_types) - set(encoder.classes_))
    if unknown_types:
        raise ValueError(
            "Unknown material_type values: "
            + ", ".join(unknown_types)
            + ". Allowed values: "
            + ", ".join(map(str, encoder.classes_))
        )

    frame["material_type_encoded"] = encoder.transform(incoming_types)
    return frame


def _score_materials(frame: pd.DataFrame, resources: dict[str, Any]) -> pd.DataFrame:
    model_frame = frame.copy()
    X = model_frame[FEATURE_COLUMNS]
    X_scaled = resources["scaler"].transform(X)

    model_frame["predicted_cost"] = resources["cost_model"].predict(X_scaled)
    model_frame["predicted_co2"] = resources["co2_model"].predict(X_scaled)

    model_frame["eco_score"] = (
        0.4 * model_frame["biodegradability_score"]
        + 0.3 * model_frame["recyclability_percentage"]
        - 0.2 * model_frame["predicted_co2"]
        - 0.1 * model_frame["predicted_cost"]
    )
    return model_frame.sort_values(by="eco_score", ascending=False).reset_index(drop=True)


def _format_material(row: pd.Series) -> dict[str, Any]:
    return {
        "material_name": row.get("material_name", "Custom Material"),
        "material_type": row["material_type"],
        "predicted_cost": round(float(row["predicted_cost"]), 4),
        "predicted_co2": round(float(row["predicted_co2"]), 4),
        "eco_score": round(float(row["eco_score"]), 4),
    }


try:
    RESOURCES = _load_resources()
    STARTUP_ERROR = None
except Exception as exc:  # pragma: no cover
    RESOURCES = None
    STARTUP_ERROR = str(exc)


@app.get("/health")
def health() -> Any:
    if STARTUP_ERROR:
        return jsonify({"status": "error", "message": STARTUP_ERROR}), 500

    dataset = RESOURCES["dataset"]
    return jsonify(
        {
            "status": "ok",
            "dataset_rows": int(len(dataset)),
            "dataset_columns": list(dataset.columns),
            "resources": RESOURCES["paths"],
        }
    )


@app.get("/metadata/material-types")
def material_types() -> Any:
    if STARTUP_ERROR:
        return jsonify({"error": STARTUP_ERROR}), 500

    classes = sorted(str(value) for value in RESOURCES["encoder"].classes_)
    return jsonify({"material_types": classes, "count": len(classes)})


@app.get("/recommend")
def recommend_from_dataset() -> Any:
    if STARTUP_ERROR:
        return jsonify({"error": STARTUP_ERROR}), 500

    ranked = _score_materials(RESOURCES["dataset"], RESOURCES)
    best = ranked.iloc[0]

    return jsonify(
        {
            "source": "dataset",
            "best_material": _format_material(best),
            "top_5": [_format_material(row) for _, row in ranked.head(5).iterrows()],
        }
    )


@app.post("/recommend")
def recommend_from_payload() -> Any:
    if STARTUP_ERROR:
        return jsonify({"error": STARTUP_ERROR}), 500

    payload = request.get_json(silent=True) or {}
    materials = payload.get("materials")

    if not isinstance(materials, list):
        return jsonify({"error": "Request body must include 'materials' as a list"}), 400

    try:
        prepared = _validate_and_prepare_materials(materials, RESOURCES["encoder"])
        ranked = _score_materials(prepared, RESOURCES)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Failed to score materials: {exc}"}), 500

    best = ranked.iloc[0]
    return jsonify(
        {
            "source": "request_payload",
            "best_material": _format_material(best),
            "ranked_materials": [_format_material(row) for _, row in ranked.iterrows()],
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

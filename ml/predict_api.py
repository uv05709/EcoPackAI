# ============================================
# EcoPackAI - AI Prediction API
# ============================================

from flask import Flask, jsonify
import joblib
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

# Load models
cost_model = joblib.load(MODELS_DIR / "cost_model.pkl")
co2_model = joblib.load(MODELS_DIR / "co2_model.pkl")
scaler = joblib.load(MODELS_DIR / "scaler.pkl")

# Load dataset
df = pd.read_csv(BASE_DIR / "dataset" / "engineered_materials.csv")

le = LabelEncoder()
df["material_type_encoded"] = le.fit_transform(df["material_type"])

features = [
    "strength_rating",
    "weight_capacity",
    "biodegradability_score",
    "recyclability_percentage",
    "material_type_encoded",
    "cost_efficiency_index",
    "co2_impact_index",
    "material_suitability_score",
]

@app.route("/recommend", methods=["GET"])
def recommend():

    X = df[features]
    X_scaled = scaler.transform(X)

    df["predicted_cost"] = cost_model.predict(X_scaled)
    df["predicted_co2"] = co2_model.predict(X_scaled)

    df["eco_score"] = (
        0.4 * df["biodegradability_score"] +
        0.3 * df["recyclability_percentage"] -
        0.2 * df["predicted_co2"] -
        0.1 * df["predicted_cost"]
    )

    best = df.sort_values(by="eco_score", ascending=False).iloc[0]

    return jsonify({
        "material_name": best["material_name"],
        "material_type": best["material_type"],
        "predicted_cost": float(best["predicted_cost"]),
        "predicted_co2": float(best["predicted_co2"]),
        "eco_score": float(best["eco_score"])
    })

if __name__ == "__main__":
    app.run(debug=True)

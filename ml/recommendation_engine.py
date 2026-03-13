# EcoPackAI - Simple AI Recommendation Script

import pandas as pd
import joblib
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

print("Starting EcoPackAI...\n")

# Get current folder
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"

def main():
    try:
        # Load trained models
        cost_model = joblib.load(MODELS_DIR / "cost_model.pkl")
        co2_model = joblib.load(MODELS_DIR / "co2_model.pkl")
        scaler = joblib.load(MODELS_DIR / "scaler.pkl")

        # Load dataset
        df = pd.read_csv(BASE_DIR / "dataset" / "engineered_materials.csv")

        if df.empty:
            print("Dataset is empty!")
            return

        # Encode material type
        le = LabelEncoder()
        df["material_type_encoded"] = le.fit_transform(df["material_type"])

        # Select features
        features = [
            "strength_rating",
            "weight_capacity",
            "biodegradability_score",
            "recyclability_percentage",
            "material_type_encoded"
        ]

        # Check if features exist
        for feature in features:
            if feature not in df.columns:
                print("Missing feature:", feature)
                return

        X = df[features]

        # Scale features
        X_scaled = scaler.transform(X)

        # Make predictions
        df["predicted_cost"] = cost_model.predict(X_scaled)
        df["predicted_co2"] = co2_model.predict(X_scaled)

        # Calculate eco score
        df["eco_score"] = (
            0.4 * df["biodegradability_score"] +
            0.3 * df["recyclability_percentage"] -
            0.2 * df["predicted_co2"] -
            0.1 * df["predicted_cost"]
        )

        # Sort by eco score
        best_material = df.sort_values(by="eco_score", ascending=False).iloc[0]

        print("Best Packaging Recommendation:\n")
        print("Material Name :", best_material["material_name"])
        print("Material Type :", best_material["material_type"])
        print("Predicted Cost:", round(best_material["predicted_cost"], 2))
        print("Predicted CO2 :", round(best_material["predicted_co2"], 2))
        print("Eco Score     :", round(best_material["eco_score"], 2))

        print("\nDone!")

    except Exception as e:
        print("Something went wrong:", e)


if __name__ == "__main__":
    main()

# ============================================
# EcoPackAI - ML Dataset Preparation
# ============================================

from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

print("\nLoading Engineered Dataset...\n")

# Resolve paths from this script location so execution is cwd-independent.
BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset" / "engineered_materials.csv"
MODELS_DIR = BASE_DIR / "models"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

# Load engineered dataset
df = pd.read_csv(DATASET_PATH)

print("Dataset Preview:")
print(df.head())

print("\nColumns in Dataset:")
print(df.columns)

# --------------------------------------------
# ENCODE CATEGORICAL FEATURES
# --------------------------------------------

print("\nEncoding Categorical Features...\n")

le = LabelEncoder()

df["material_type_encoded"] = le.fit_transform(df["material_type"])

print("Encoded material_type successfully.")

# --------------------------------------------
# SELECT FEATURES FOR ML MODEL
# --------------------------------------------

print("\nSelecting ML Features...\n")

features = [
    "strength_rating",
    "weight_capacity",
    "biodegradability_score",
    "recyclability_percentage",
    "material_type_encoded",
]

X = df[features]

# Targets
y_cost = df["cost_per_unit"]
y_co2 = df["co2_emission_score"]

print("Feature Matrix Shape:", X.shape)

# --------------------------------------------
# TRAIN TEST SPLIT (80-20)
# --------------------------------------------

print("\nSplitting Dataset into Train & Test...\n")

(
    X_train,
    X_test,
    y_cost_train,
    y_cost_test,
    y_co2_train,
    y_co2_test,
) = train_test_split(X, y_cost, y_co2, test_size=0.2, random_state=42)

print("Training Set Size:", X_train.shape)
print("Testing Set Size:", X_test.shape)

# --------------------------------------------
# FEATURE SCALING
# --------------------------------------------

print("\nApplying Feature Scaling...\n")

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# --------------------------------------------
# SAVE SCALER & SPLIT DATASETS
# --------------------------------------------

MODELS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
print("\nScaler Saved Successfully!")

joblib.dump(X_train_scaled, ARTIFACTS_DIR / "X_train.pkl")
joblib.dump(X_test_scaled, ARTIFACTS_DIR / "X_test.pkl")
joblib.dump(y_cost_train, ARTIFACTS_DIR / "y_cost_train.pkl")
joblib.dump(y_cost_test, ARTIFACTS_DIR / "y_cost_test.pkl")
joblib.dump(y_co2_train, ARTIFACTS_DIR / "y_co2_train.pkl")
joblib.dump(y_co2_test, ARTIFACTS_DIR / "y_co2_test.pkl")

print("\nTrain-Test Datasets Saved!")

print("\nML Dataset Preparation Completed Successfully!")

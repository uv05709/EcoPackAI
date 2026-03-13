# ============================================
# EcoPackAI - Feature Engineering Module
# ============================================

import pandas as pd
import numpy as np
import os
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

print("\nConnecting to PostgreSQL Database...\n")

# --------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------
database_url = os.getenv("DATABASE_URL")
if not database_url:
    database_url = (
        f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', '')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'ecopackai')}"
    )

engine = create_engine(database_url)

# --------------------------------------------
# LOAD MATERIALS DATA
# --------------------------------------------
print("Loading Materials Dataset...\n")

df = pd.read_sql("SELECT * FROM materials", engine)

print("Initial Dataset Preview:")
print(df.head())

print("\nDataset Info:")
print(df.info())

# --------------------------------------------
# HANDLE MISSING VALUES
# --------------------------------------------
print("\nChecking Missing Values:\n")
print(df.isnull().sum())

df.fillna({
    "strength_rating": df["strength_rating"].mean(),
    "weight_capacity": df["weight_capacity"].mean(),
    "biodegradability_score": df["biodegradability_score"].mean(),
    "recyclability_percentage": df["recyclability_percentage"].mean(),
    "co2_emission_score": df["co2_emission_score"].mean(),
    "cost_per_unit": df["cost_per_unit"].mean()
}, inplace=True)

# Remove duplicates if any
df.drop_duplicates(inplace=True)

print("\nMissing Values After Cleaning:\n")
print(df.isnull().sum())

# --------------------------------------------
# FEATURE ENGINEERING STARTS HERE
# --------------------------------------------

print("\nPerforming Feature Engineering...\n")

# 1️⃣ CO2 Impact Index
df["co2_impact_index"] = (
    df["co2_emission_score"] * 10
    / df["recyclability_percentage"]
)

# 2️⃣ Cost Efficiency Index
df["cost_efficiency_index"] = (
    df["strength_rating"]
    / df["cost_per_unit"]
)

# 3️⃣ Load Product Category Data
product_df = pd.read_sql("SELECT * FROM product_categories", engine)

# Encode Fragility Levels
fragility_map = {
    "Low": 1,
    "Medium": 2,
    "High": 3
}

product_df["fragility_score"] = product_df["fragility_level"].map(fragility_map)

print("\nProduct Category Data Preview:")
print(product_df.head())

# 4️⃣ Material Suitability Score
df["material_suitability_score"] = (
    0.4 * df["strength_rating"] +
    0.3 * df["biodegradability_score"] +
    0.2 * df["recyclability_percentage"] -
    0.1 * df["co2_emission_score"]
)


print("\nEngineered Dataset Summary Statistics:\n")
print(df.describe())


df.to_csv("ml/dataset/engineered_materials.csv", index=False)

print("\nFeature Engineered Dataset Saved Successfully!")

print("File: ml/dataset/engineered_materials.csv")


print("\nFeature Engineering Completed Successfully!")

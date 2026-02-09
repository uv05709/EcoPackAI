import pandas as pd
import psycopg2

# Database connection
conn = psycopg2.connect(
    dbname="ecopackai",
    user="postgres",
    password="123456789",
    host="localhost",
    port="5432"
)

# Load materials data
query = "SELECT * FROM materials;"
df = pd.read_sql(query, conn)

print(df.head())
print(df.info())
# Check missing values
print(df.isnull().sum())

# Handle missing values
df.fillna({
    "strength_rating": df["strength_rating"].mean(),
    "biodegradability_score": df["biodegradability_score"].mean(),
    "recyclability_percentage": df["recyclability_percentage"].mean()
}, inplace=True)

# Remove duplicates
df.drop_duplicates(inplace=True)



df["co2_impact_index"] = (
    df["co2_emission_score"] * 10 / df["recyclability_percentage"]
)
df["cost_efficiency_index"] = (
    df["strength_rating"] / df["cost_per_unit"]
)
df["material_suitability_score"] = (
    0.4 * df["strength_rating"] +
    0.3 * df["biodegradability_score"] +
    0.2 * df["recyclability_percentage"] -
    0.1 * df["co2_emission_score"]
)
print(df.describe())


df.to_csv("ml/dataset/cleaned_materials.csv", index=False)

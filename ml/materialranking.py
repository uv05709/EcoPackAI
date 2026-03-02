import pandas as pd

df = pd.read_csv("ml/dataset/engineered_materials.csv")

df["sustainability_score"] = (
    0.5 * df["cost_efficiency_index"] +
    0.5 * df["co2_impact_index"]
)

df = df.sort_values(by="sustainability_score")

print(df.head())
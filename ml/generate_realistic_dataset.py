import pandas as pd
import numpy as np

df_base = pd.read_csv("ml/dataset/real_materials_base.csv")

expanded_data = []

# 28 × 25 ≈ 700 rows
for _ in range(28):
    for _, row in df_base.iterrows():
        new_row = row.copy()

        # Controlled realistic variation
        new_row["strength_rating"] += np.random.randint(-1, 2)
        new_row["weight_capacity"] += np.random.uniform(-5, 5)
        new_row["biodegradability_score"] += np.random.randint(-1, 2)
        new_row["recyclability_percentage"] += np.random.randint(-5, 5)
        new_row["co2_emission_score"] += np.random.uniform(-0.7, 0.7)
        new_row["cost_per_unit"] += np.random.uniform(-3, 3)

        # Clip realistic ranges
        new_row["strength_rating"] = np.clip(new_row["strength_rating"], 1, 10)
        new_row["biodegradability_score"] = np.clip(new_row["biodegradability_score"], 1, 10)
        new_row["recyclability_percentage"] = np.clip(new_row["recyclability_percentage"], 0, 100)

        expanded_data.append(new_row)

df_large = pd.DataFrame(expanded_data)

print("Total Records Generated:", len(df_large))

df_large.to_csv("ml/dataset/materials.csv", index=False)

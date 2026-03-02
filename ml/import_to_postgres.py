import pandas as pd
from sqlalchemy import create_engine

# Load the generated dataset
df = pd.read_csv("ml/dataset/materials.csv")

# Database connection
engine = create_engine("postgresql://postgres:123456789@localhost:5432/ecopackai")

# Replace old table data
df.to_sql("materials", engine, if_exists="replace", index=False)

print("Data successfully inserted into PostgreSQL")
print("Total rows inserted:", len(df))

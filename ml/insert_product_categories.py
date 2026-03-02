import pandas as pd
from sqlalchemy import create_engine

# Load dataset
df = pd.read_csv("ml/dataset/product_categories.csv")

# DB connection
engine = create_engine("postgresql://postgres:123456789@localhost:5432/ecopackai")

# Insert into PostgreSQL
df.to_sql("product_categories", engine, if_exists="replace", index=False)

print("Product categories inserted successfully")
print("Total rows inserted:", len(df))

import pandas as pd
import os
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Load dataset
df = pd.read_csv("ml/dataset/product_categories.csv")

# DB connection
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

# Insert into PostgreSQL
df.to_sql("product_categories", engine, if_exists="replace", index=False)

print("Product categories inserted successfully")
print("Total rows inserted:", len(df))

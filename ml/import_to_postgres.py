import pandas as pd
import os
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Load the generated dataset
df = pd.read_csv("ml/dataset/materials.csv")

# Database connection
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

# Replace old table data
df.to_sql("materials", engine, if_exists="replace", index=False)

print("Data successfully inserted into PostgreSQL")
print("Total rows inserted:", len(df))

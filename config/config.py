from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()

DB_HOST = os.getenv("DB_HOST") or os.getenv("POSTGRES_HOST") or "postgres"
DB_PORT = int(os.getenv("DB_PORT") or os.getenv("POSTGRES_PORT") or "5432")
DB_NAME = os.getenv("DB_NAME") or os.getenv("POSTGRES_DB") or "postgres"
DB_USER = os.getenv("POSTGRES_USER") or "postgres"
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD") or "postgres"

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)


#Project Directories
BASE_DIR = Path(__file__).resolve().parent.parent #project root

DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

#Customer Care Emails
EMAILS_DATASET_PATH = DATA_DIR /  "dataset.csv"
EMAILS_SCHEMA_PATH = CONFIG_DIR / "customer-care-emails" / "expected_schema.yaml"
EMAILS_DDL_PATH = CONFIG_DIR / "customer-care-emails" / "ddl.sql"
from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME"),
)


#Project Directories
BASE_DIR = Path(__file__).resolve().parent.parent #project root

DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

#Customer Care Emails
EMAILS_DATASET_PATH = DATA_DIR /  "dataset.csv"
EMAILS_SCHEMA_PATH = CONFIG_DIR / "customer-care-emails" / "expected_schema.yaml"
EMAILS_DDL_PATH = CONFIG_DIR / "customer-care-emails" / "ddl.sql"
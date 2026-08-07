from pathlib import Path

#Project Directories
BASE_DIR = Path(__file__).resolve().parent.parent #project root

DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

#Customer Care Emails
EMAILS_DATASET_PATH = DATA_DIR /  "dataset.csv"
EMAILS_SCHEMA_PATH = CONFIG_DIR / "customer-care-emails" / "expected_schema.yaml"
EMAILS_DDL_PATH = CONFIG_DIR / "customer-care-emails" / "ddl.sql"
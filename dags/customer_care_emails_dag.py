# orchestrate the pipeline

from datetime import datetime
from pathlib import Path

from airflow.decorators import dag, task
from pandas import DataFrame

from config.config import (
    DATABASE_URL,
    EMAILS_DDL_PATH,
    EMAILS_DATASET_PATH,
    EMAILS_SCHEMA_PATH,
)
from pipeline.extract import extract_csv
from pipeline.load import load_to_postgres
from pipeline.transform import transform_data
from pipeline.validation import load_yaml_to_dict, validate_df_schema


#set airflow staging directory for temporary data storage for data communication between isolated tasks
STAGING_DIR = Path("/tmp/airflow_staging/customer_care_emails")

@dag(
    dag_id="customer_care_emails_pipeline",
    schedule="@daily",
    start_date=datetime(2026, 8, 1),
    catchup=False,
    default_args={"owner": "airflow"},
)
def customer_care_emails_etl_orchestrator():
    """ETL pipeline for customer care email ingestion."""

    @task
    def extract(file_path: str | Path = EMAILS_DATASET_PATH) -> str:
        """Extracts CSV data, writes to staging Parquet, and returns the path."""
        STAGING_DIR.mkdir(parents=True, exist_ok=True)
        staging_path = STAGING_DIR / "extracted_data.parquet"

        #extract raw data into memory temporarily
        df = extract_csv(file_path)

        #persis data to disk (staging area)
        df.to_parquet(staging_path, index=False)
        return str(staging_path)

    @task
    def validate(extracted_path: str, schema_path: str | Path = EMAILS_SCHEMA_PATH) -> str:
        """Reads staged file, validates schema, and passes the path forward."""
        extracted_df = pd.read_parquet(extracted_path)
        validate_df_schema(extracted_df, schema_path)
        #return the path to the validated data
        return extracted_path

    @task
    def transform(validated_path: str) -> str:
        """Reads validated dataset, transforms data, and writes to a new staging file."""
        df = pd.read_parquet(validated_path)
        transformed_df = transform_data(df)
        staging_path = STAGING_DIR / "transformed_data.parquet"
        return str(staging_path)

    @task
    def load(transformed_path: str) -> int:
        """Loads final Parquet dataset into PostgreSQL. Returns #rows loaded"""
        SCHEMA = load_yaml_to_dict(EMAILS_SCHEMA_PATH)
        TABLE = SCHEMA["table"]
        df = pd.read_parquet(transformed_path)
        rows_loaded =  load_to_postgres(
            transformed_df,
            DATABASE_URL,
            TABLE,
            ddl_path=EMAILS_DDL_PATH,
        )
        return rows_loaded

    #define task dependencies (implicitly) and build the DAG nodes 
    #implicit dependency: extract >> validate >> transfrom >> load 
    # Execution Flow: Implicit dependencies passing file path strings
    raw_path = extract(EMAILS_DATASET_PATH)
    validated_path = validate(raw_path, EMAILS_SCHEMA_PATH)
    transformed_path = transform(validated_path)
    load(transformed_path)
    

#create the DAG 
customer_care_emails_etl_orchestrator()


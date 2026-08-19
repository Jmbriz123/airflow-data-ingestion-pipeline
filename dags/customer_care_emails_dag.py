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

SCHEMA = load_yaml_to_dict(EMAILS_SCHEMA_PATH)
TABLE = SCHEMA["table"]


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
    def extract(file_path: str | Path = EMAILS_DATASET_PATH) -> DataFrame:
        return extract_csv(file_path)

    @task
    def validate(extracted_df: DataFrame, schema_path: str | Path = EMAILS_SCHEMA_PATH) -> DataFrame:
        validate_df_schema(extracted_df, schema_path)
        return extracted_df

    @task
    def transform(validated_df: DataFrame) -> DataFrame:
        return transform_data(validated_df)

    @task
    def load(transformed_df: DataFrame) -> int:
        return load_to_postgres(
            transformed_df,
            DATABASE_URL,
            TABLE,
            ddl_path=EMAILS_DDL_PATH,
        )

    #define task dependencies (implicitly) and build the DAG nodes 
    extracted_data = extract(EMAILS_DATASET_PATH)
    validated_data = validate(extracted_data, EMAILS_SCHEMA_PATH)
    transformed_data = transform(validated_data)
    load(transformed_data)

    


customer_care_emails_etl_orchestrator()


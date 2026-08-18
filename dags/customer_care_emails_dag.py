#orchestrate the pipeline

from airflow.sdk import dag, task
from datetime import datetime
#imports all the pipeline scripts inside pipeline/ package
from pipeline.extract import extract_csv
from pipeline.validation import validate_df_schema
from pipeline.transform import transform_data 
from pipeline.load import load_to_postgres

from config.config import (   
    DATABASE_URL,
    EMAILS_DDL_PATH,
    EMAILS_DATASET_PATH,
    EMAILS_SCHEMA_PATH,
)

from pathlib import Path
from pandas import DataFrame

#workflow definition
@dag(
    dag_id = "customer_care_emails_pipeline",
    schedule = "@daily",
    start_date = datetime(2026, 8, 1),
    catchup = False #to avoid creating historizal scheduled runs for the missed periods
)
def customer_care_emails_etl_orchestrator():
    
    #define DAG nodes/task
    @task 
    def extract(file_path: Path  = EMAILS_DATASET_PATH) -> DataFrame:
        return extract_csv(file_path)

    @task
    def validate(extracted_df: DataFrame, schema_path: Path = EMAILS_DATASET_PATH):
        return validate_df_schema(extracted_df, schema_path)

    @task
    def transform(validated_df: DataFrame) -> DataFrame:
        return transform_data(validated_df)

    @task
    def load(transformed_df: DataFrame, db_uri: str, table_name: str, ddl_path: str | Path | None = None) -> int:
        return load_to_postgres(transformed_df)

    #define task dependencies
    
    




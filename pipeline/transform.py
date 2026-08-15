import logging
import pandas as pd
import json
from pandas import DataFrame

from config.paths import EMAILS_DATASET_PATH, EMAILS_SCHEMA_PATH
#import ETL functions 
from pipeline.extract import extract_csv
from pipeline.validation import validate_df_schema
# Set up module logger
logger = logging.getLogger(__name__)

def transform_data(df: DataFrame) -> DataFrame: 
    """Cleans and transforms raw email DataFrame for PostgreSQL loading."""
    logger.info("Starting data transformation pipeline...")
    
    # Create a copy so we don't mutate the raw extracted DataFrame in place
    transformed_df = df.copy()
    
    # 1. Clean string column whitespace
    string_columns = transformed_df.select_dtypes(include=["object", "string"]).columns
    for col in string_columns:
        transformed_df[col] = transformed_df[col].str.strip()
    # 2. Parse timestamp column

    transformed_df['timestamp'] = pd.to_datetime(
        transformed_df['timestamp'],
        format='ISO8601', utc=True
    )

    # 3. Clean numeric columns
    transformed_df['customer_satisfaction'] = pd.to_numeric(
        transformed_df['customer_satisfaction'],
        errors="coerce"
    )
    
    # 4. Format JSON columns
    # handdle missing values
    logger.info("Data transformation completed successfully.")
    return transformed_df

def ensure_valid_json(val):
    if pd.isna(val) or val is None:
        return None 
    if isinstance(val, str):
        ...
        

if __name__ == "__main__":
    # Configure root logger output format for local execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    extracted_df = extract_csv(EMAILS_DATASET_PATH)
    validate_df_schema(extracted_df, EMAILS_SCHEMA_PATH)
    transformed_data = transform_data(extracted_df)


import logging
from pandas import DataFrame
from sqlalchemy import create_engine
import os

from pipeline.extract import extract_csv
from pipeline.validation import validate_df_schema
from pipeline.transform import transform_data
from pipeline.validation import load_yaml_to_dict
from config.config import EMAILS_DATASET_PATH, EMAILS_SCHEMA_PATH, DATABASE_URL

logger = logging.getLogger(__name__)




SCHEMA = load_yaml_to_dict(EMAILS_SCHEMA_PATH)
TABLE = SCHEMA['table']

def load_to_postgres(df: DataFrame, db_uri: str, table_name: str) -> None:
    """Loads transformed DataFrame into target PostgreSQL table."""
    logger.info(f"Starting data load into table '{table_name}'...")
    
 
    engine = create_engine(db_uri)
    # load dataframe to sql DB
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",  # Options: 'fail', 'replace', 'append'
        index=False,
        chunksize=1000,
        method="multi"
    )
    
    logger.info(f"Successfully loaded {len(df)} rows into '{table_name}'.")



if __name__ == "__main__":
    # Configure root logger output format for local execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    extracted_df = extract_csv(EMAILS_DATASET_PATH)
    validate_df_schema(extracted_df, EMAILS_SCHEMA_PATH)
    transformed_data = transform_data(extracted_df)
    load_to_postgres(transformed_data, DATABASE_URL, TABLE)


import logging
from pathlib import Path

from pandas import DataFrame
from sqlalchemy import create_engine, text

from config.config import (
    DATABASE_URL,
    EMAILS_DDL_PATH,
    EMAILS_DATASET_PATH,
    EMAILS_SCHEMA_PATH,
)
from pipeline.extract import extract_csv
from pipeline.transform import transform_data
from pipeline.validation import load_yaml_to_dict, validate_df_schema

logger = logging.getLogger(__name__)

SCHEMA = load_yaml_to_dict(EMAILS_SCHEMA_PATH)
TABLE = SCHEMA["table"]


def split_schema_and_table(table_name: str) -> tuple[str, str]:
    """Return (schema_name, table_name) for a qualified SQL table reference."""
    if "." in table_name:
        schema_name, table = table_name.rsplit(".", 1)
        return schema_name, table
    return "public", table_name


def ensure_table_exists(engine, ddl_path: str | Path) -> None:
    """Create the target table using the project DDL if it does not already exist."""
    ddl_sql = Path(ddl_path).read_text(encoding="utf-8")
    with engine.begin() as connection:
        connection.execute(text(ddl_sql))
    logger.info("Ensured target table exists in PostgreSQL.")


def load_to_postgres(df: DataFrame, db_uri: str, table_name: str, ddl_path: str | Path | None = None) -> int:
    """Load a transformed DataFrame into PostgreSQL using a schema-aware, transaction-safe insert."""
    schema_name, actual_table_name = split_schema_and_table(table_name)
    logger.info(f"Starting data load into table '{schema_name}.{actual_table_name}'...")

    engine = create_engine(db_uri)

    if ddl_path is not None:
        ensure_table_exists(engine, ddl_path)

    with engine.begin() as connection:
        df.to_sql(
            name=actual_table_name,
            con=connection,
            schema=schema_name,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi",
        )

    row_count = len(df)
    logger.info(f"Successfully loaded {row_count} rows into '{schema_name}.{actual_table_name}'.")
    engine.dispose()
    return row_count


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    extracted_df = extract_csv(EMAILS_DATASET_PATH)
    validate_df_schema(extracted_df, EMAILS_SCHEMA_PATH)
    transformed_data = transform_data(extracted_df)
    load_to_postgres(transformed_data, DATABASE_URL, TABLE, ddl_path=EMAILS_DDL_PATH)


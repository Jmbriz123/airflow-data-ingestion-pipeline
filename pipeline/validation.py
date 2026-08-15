from pathlib import Path
import logging
from typing import Any, Dict

import yaml
from pandas import DataFrame

from config.paths import EMAILS_DATASET_PATH, EMAILS_SCHEMA_PATH
from pipeline.extract import extract_csv

# Initialize module-level logger
logger = logging.getLogger(__name__)

# Module-level constant mapping DB schema types to allowed Pandas dtypes
SCHEMA_TO_PANDAS_TYPES: Dict[str, list[str]] = {
    "text": ["object", "string"],
    "numeric": ["float64", "int64", "int32", "float32"],
    "jsonb": ["object", "string"],
    "timestamp with time zone": [
        "object",
        "datetime64[ns, UTC]",
        "datetime64[ns]",
    ],
}


def load_yaml_to_dict(schema_path: Path) -> Dict[str, Any]:
    """Loads and parses a YAML schema file into a dictionary."""
    logger.info(f"Loading schema from {schema_path}")
    try:
        with open(schema_path, "r", encoding="utf-8") as file:
            schema = yaml.safe_load(file)
            if not isinstance(schema, dict):
                raise ValueError(
                    f"Schema definition at {schema_path} must be a valid dictionary."
                )
            return schema
    except Exception as err:
        logger.error(f"Failed to load schema from {schema_path}: {err}")
        raise


def validate_column_names(df: DataFrame, schema: Dict[str, Any]) -> None:
    """Validates that DataFrame columns match the expected schema definition."""
    logger.info("Validating column names...")
    expected_columns = {col["name"] for col in schema.get("columns", [])}
    actual_columns = set(df.columns)

    missing_columns = expected_columns - actual_columns
    unexpected_columns = actual_columns - expected_columns

    if missing_columns or unexpected_columns:
        error_msg = (
            f"Schema mismatch detected. "
            f"Missing columns: {missing_columns or 'None'}. "
            f"Unexpected columns: {unexpected_columns or 'None'}."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info("Column name validation passed.")


def validate_column_nullability(df: DataFrame, schema: Dict[str, Any]) -> None:
    """Validates non-nullable constraints across all schema columns."""
    logger.info("Validating column nullability...")
    nullability_errors = []

    for col_def in schema.get("columns", []):
        col_name = col_def["name"]
        if not col_def.get("nullable", True) and col_name in df.columns:
            null_count = df[col_name].isna().sum()
            if null_count > 0:
                nullability_errors.append(f"'{col_name}' ({null_count} nulls)")

    if nullability_errors:
        error_msg = (
            f"Nullability constraint failed for column(s): "
            f"{', '.join(nullability_errors)}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info("Column nullability validation passed.")


def validate_column_data_type(df: DataFrame, schema: Dict[str, Any]) -> None:
    """Validates DataFrame column data types against allowed schema types."""
    logger.info("Validating column data types...")
    mismatches = []

    for col_def in schema.get("columns", []):
        col_name = col_def["name"]
        if col_name not in df.columns:
            continue

        expected_type = col_def["type"]
        actual_type = str(df[col_name].dtype)
        allowed_types = SCHEMA_TO_PANDAS_TYPES.get(expected_type, [expected_type])

        if actual_type not in allowed_types:
            mismatches.append(
                f"Column '{col_name}': expected DB type '{expected_type}' "
                f"(allowed pandas: {allowed_types}), got '{actual_type}'"
            )

    if mismatches:
        error_details = "\n".join(mismatches)
        error_msg = f"Data type validation failed:\n{error_details}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info("Column data type validation passed.")


def validate_df_schema(df: DataFrame, schema_path: Path) -> None:
    """Orchestrates end-to-end schema validation for the DataFrame."""
    logger.info(f"Starting schema validation for DataFrame shape {df.shape}")
    schema = load_yaml_to_dict(schema_path)

    validate_column_names(df, schema)
    validate_column_nullability(df, schema)
    validate_column_data_type(df, schema)

    logger.info("DataFrame schema validation passed successfully.")


if __name__ == "__main__":
    # Configure root logger output format for local execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    extracted_df = extract_csv(EMAILS_DATASET_PATH)
    validate_df_schema(extracted_df, EMAILS_SCHEMA_PATH)
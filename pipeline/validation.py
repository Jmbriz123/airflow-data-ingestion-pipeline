#purpose: validate the extracted data
#continue if valid, raise exception if not valid 
import pandas as pd 
from pandas import DataFrame
import yaml
import logging
from pathlib import Path
from pipeline.extract import extract_csv
from config.paths import EMAILS_SCHEMA_PATH
from config.paths import EMAILS_DATASET_PATH
from pprint import pprint

def validate_df_schema(df: DataFrame, schema_path: Path) ->None:
    
    #load the YAML file into python dictionary
    schema = load_YAML_to_dict(schema_path)
    
    #validate column names 
    validate_column_names(df, schema)
    #validate nullability of each columns
    validate_column_nullability(df, schema)
    #validate column data types 
    validate_column_data_type(df, schema)



def load_YAML_to_dict(schema_path: Path) -> dict:
    with open(schema_path) as file:
        schema = yaml.safe_load(file)
    return  schema
def validate_column_names(df: DataFrame, schema: dict) ->None: 
     #Expected Columns
    expected_columns = { #extract column names from the schema columns
        column["name"]
        for column in schema["columns"]
    }
    #actual columns
    actual_columns = set(df.columns)

    #compare columns by looking at set difference
    missing_columns = expected_columns - actual_columns
    unexpected_columns = actual_columns - expected_columns

    
    #validate column names
    if missing_columns or unexpected_columns:
        raise ValueError(
            f"Schema Mismatch. "
            f"Missing columns: {missing_columns}. "
            f"Unexpected columns: {unexpected_columns}. "
        )
    else:
        print("Column names validation passed")

def validate_column_nullability(df: DataFrame, schema: dict) ->None : #validate nullability of each columns in the df
    for column in schema['columns']:
        if column['nullable'] is False:
            if df[column['name']].isna().any():
                raise ValueError(f"Incoming dataframe column did not match expected nullability")
    print("Column nullability validation passeed")

def validate_column_data_type(df: DataFrame, schema: dict) -> None:
    # 1. Create a list to store mismatch messages
    mismatches = []
    #data type mapping
    SCHEMA_TO_PANDAS_TYPES = {
        "text": ["object", "string"],
        "numeric": ["float64", "int64"],
        "jsonb": ["object", "string"],
        "timestamp with time zone": ["object", "datetime64[ns, UTC]", "datetime64[ns]"],
    }
    # 2. Loop over columns in schema and df 
    for column in schema["columns"]:
        col_name = column["name"]

        # Get the expected type string from the 'column' dict
        expected_type = column['type']

        # Get the actual dtype from the DataFrame
        actual_type = str(df[col_name].dtype)

        #allowed pandas types for this schema type
        allowed_types = SCHEMA_TO_PANDAS_TYPES.get(expected_type, [expected_type])

        #check if actual types matches allowed types
        if actual_type not in allowed_types:
            mismatches.append(
                f"Column '{col_name}': expected DB type '{expected_type}' "
                f"(allowed: {allowed_types}), got '{actual_type}'"
            )


    if mismatches:
        # Joining the mismatch list with newlines makes debugging super easy in terminal/logs
        error_details = "\n".join(mismatches)
        raise ValueError(f"Data type validation failed:\n{error_details}")
    else:
        print("Column data type validation passed.")

if __name__ == "__main__":

    validate_df_schema(extract_csv(EMAILS_DATASET_PATH), EMAILS_SCHEMA_PATH)


    
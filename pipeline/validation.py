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


if __name__ == "__main__":

    validate_df_schema(extract_csv(EMAILS_DATASET_PATH), EMAILS_SCHEMA_PATH)


    
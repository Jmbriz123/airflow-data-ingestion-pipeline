#purpose: validate the extracted data
#continue if valid, raise exception if not valid 
import pandas as pd 
import yaml
import logging

from pipeline.extract import extract_csv
from config.paths import EMAILS_SCHEMA_PATH
from config.paths import EMAILS_DATASET_PATH
from pprint import pprint
def validate_schema(df, schema_path):
    
    #load the YAML file into python dictionary
    schema = load_YAML_to_dict(schema_path)
    
    #validate column names 
    validate_columns(df, schema)
    #validate nullability of each columns



def load_YAML_to_dict(schema_path):
    with open(schema_path) as file:
        schema = yaml.safe_load(file)
    return  schema
def validate_columns(df, schema):
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


if __name__ == "__main__":
    validate_schema(extract_csv(EMAILS_DATASET_PATH), EMAILS_SCHEMA_PATH)


    
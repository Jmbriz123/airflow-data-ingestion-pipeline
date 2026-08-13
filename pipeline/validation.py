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
    with open(schema_path) as file:
        schema = yaml.safe_load(file) 
    
    #Expected Columns
    expected_columns = [ #extract column names from the schema columns
        column["name"]
        for column in schema["columns"]
    ]
    #actual columns
    actual_columns = list(df.columns)

    #validate column names
    if actual_columns != expected_columns:
        raise ValueError("CSV columns do not match expected schema")
    else:
        print("Actual column names match the expected")


if __name__ == "__main__":
    validate_schema(extract_csv(EMAILS_DATASET_PATH), EMAILS_SCHEMA_PATH)


    
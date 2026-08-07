#purpose: validate the extracted data
#continue if valid, raise exception if not valid 
import pandas as pd 
import yaml
import logging

from pipeline.extract import extract_csv
from config.paths import EMAILS_SCHEMA_PATH
from config.paths import EMAILS_DATASET_PATH
def validate_schema(df, schema_path):
    
    #load the YAML file into python dictionary
    with open(schema_path) as file:
        schema = yaml.safe_load(file) 
    print(schema)


if __name__ == "__main__":
    validate_schema(extract_csv(EMAILS_DATASET_PATH), EMAILS_SCHEMA_PATH)
    
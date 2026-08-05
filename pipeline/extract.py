#script purpose: extractr and read the CSV data source
# Input: daset.csv
# Output: Pandas DataFrame
import pandas as pd 
from pandas import DataFrame


def extract_csv(file_path: str) -> DataFrame:
    df = pd.read_csv(file_path)
    print(df)
    return df



extract_csv("data/dataset.csv")
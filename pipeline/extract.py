#script purpose: extractr and read the CSV data source
# Input: daset.csv
# Output: Pandas DataFrame
import pandas as pd 
from pandas import DataFrame
from pathlib import Path
def extract_csv(file_path: Path) -> DataFrame:
    df = pd.read_csv(file_path)
    print(df)
    return df

BASE_DIR = Path(__file__).resolve().parent.parent #project root
DATA_PATH = BASE_DIR / "data" / "dataset.csv"

if __name__ == "__main__":
    extract_csv(DATA_PATH)
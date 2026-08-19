#script purpose: extractr and read the CSV data source
# Input: daset.csv
# Output: Pandas DataFrame
import pandas as pd 
from pandas import DataFrame
from pathlib import Path
import logging
from config.config import EMAILS_DATASET_PATH
#configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

#create logger for this module 
logger = logging.getLogger(__name__)

def extract_csv(file_path: Path) -> DataFrame:
    logger.info("Starting CSV extraction.")

    try:
        logger.info(f"Reading CSV from {file_path}")

        df = pd.read_csv(file_path)

        logger.info(
            f"Extracted {len(df)} rows and {len(df.columns)} columns"
        )

        logger.info("CSV extraction completed")

        return df

    except FileNotFoundError:
        logger.exception(f"CSV file not found: {file_path}")
        raise




if __name__ == "__main__":
    extract_csv(EMAILS_DATASET_PATH) 
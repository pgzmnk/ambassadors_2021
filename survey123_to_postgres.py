"""Extract Survey123 table and load onto Postgres db.
Note: create a directory named `survey123/` at the same level as this file.
"""

import os
import shutil

from arcgis.apps.survey123 import SurveyManager, Survey
from arcgis.gis import GIS
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

load_dotenv()


USER_NAME = os.getenv('SURVEY123_USER_NAME', None)
PASSWORD = os.getenv('SURVEY123_PASSWORD', None)
SURVEY_ID = '21a05e4038314f6c9c8fd88485c9eef3'
OUTPUT_DIR = 'survey123/'


def create_survey123_dataframe():
    """Extract survey123 table and return it as a DataFrame.
    """
    # Credentials
    gis = GIS("https://12csi.maps.arcgis.com/", USER_NAME, PASSWORD)
 #   print(f"Connected to {gis.properties.portalHostname} as {gis.users.me.username}")

    # Get the report
    sm = SurveyManager(gis)
    report = sm.get(SURVEY_ID)

    # Download the report data as CSV
    arr1 = os.listdir(OUTPUT_DIR)
    report.download(export_format='csv', save_folder=OUTPUT_DIR)
  #  print("Downloaded report.")

    # Select newly added `.zip`
    arr2 = os.listdir(OUTPUT_DIR)
    target_zip = (set(arr2)-set(arr1)).pop()

    # Unpack `.zip`
    shutil.unpack_archive(os.path.join(OUTPUT_DIR,target_zip), OUTPUT_DIR)

    # Create df
    target_csv = os.path.join(OUTPUT_DIR, 'survey_0.csv')

    return pd.read_csv(target_csv)

def load_to_postgres(df, table_name='survey_raw'):
    """Load DataFrame to Postgres db.
    """

    # Establish connection to Postgres db
    engine = create_engine(os.getenv('POSTGRES_CONNECTION'))

    # Write dataframe to db with table name `surver_raw_table_name` (OVERWRITES)
    df.to_sql(table_name, engine, if_exists='replace')

  #  print(df.head())
   # print('Succesfully wrote to DB.')


if __name__=="__main__":
    df = create_survey123_dataframe()
    load_to_postgres(df)
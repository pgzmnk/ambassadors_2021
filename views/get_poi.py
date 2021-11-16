# SQLAlchemy creates an engine that connects Pandas with a Postgres database
# Documentation: https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html
# !pip install SQLAlchemy
import os

from dotenv import load_dotenv
import json
import pandas as pd
from sqlalchemy import create_engine
from shapely.geometry import shape
import pandas as pd
import geopandas as gpd


# Load environment variables
load_dotenv()

# Establish connection to Postgres db
engine = create_engine(os.getenv('POSTGRES_CONNECTION', None))

def get_places_geoenriched():

    
    # Read SQL table with pandas
    
    df_places = pd.read_sql("SELECT * FROM places_2021", engine)
    # Convert geometry from string to json
    df_places['geometry_as_json'] = df_places['geometry'].apply(json.loads)
    # Convert places Pandas dataframe to GeoPandas

    # Pandas to GeoPandas
    gdf_places = gpd.GeoDataFrame(df_places)

    # Set geometry column
    gdf_places['geometry'] = gpd.GeoDataFrame({'geometry':[shape(i) for i in df_places['geometry_as_json']]}).values
    return gdf_places


def get_events_geoenriched():
    df_events = pd.read_sql("SELECT * FROM survey_raw", engine)
    # Convert events Pandas data frame to GeoPandas
    gdf_events = gpd.GeoDataFrame(df_events, geometry=gpd.points_from_xy(df_events.x, df_events.y))
    return gdf_events

def join_places_points(gdf_events, gdf_places):
    gdf_events_geoenriched=gpd.sjoin(gdf_events.head(),gdf_places.head(),how='left',op='within')
    gdf_events_geoenriched = gdf_events_geoenriched.drop(['type', 'properties', 'geometry_as_json'], axis=1)
    return gdf_events_geoenriched


def preview_data(df):
    print(df)

if __name__ == '__main__':
    df_places = get_places_geoenriched()
    df_events = get_events_geoenriched()
    df_output = join_places_points(df_events, df_places)
    
    preview_data(df_output)
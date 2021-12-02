import os

from dotenv import load_dotenv
import geopandas as gpd
import get_poi
import pandas as pd
from sqlalchemy import create_engine


# Load environment variables
load_dotenv()


def preprocess_and_load_survey_df():
    """Extract and preprocess survey data
    """

    # SQLAlchemy creates an engine that connects Pandas with a Postgres database
    # Documentation: https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html

    # Establish connection to Postgres db
    engine = create_engine(os.getenv('POSTGRES_CONNECTION', None))

    # Read SQL table with pandas
    df_all = pd.read_sql("SELECT * FROM survey_raw", engine)
#    print(df_all.columns)
    # clean the column names
    # PLEASE NOTE WE DELETED THE FIRST COLUMN LABELED ASSESSMENT SINCE THERE IS NO DATA IN THIS COLUMN
    cleaned_column_names = (df_all.columns
                            .str.strip()
                            .str.replace('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', regex=True)
                            .str.lower()
                            .str.replace('[ _-]+', '_', regex=True)
                            .str.replace('[}{)(><.!?\\\\:;,-]', '', regex=True))
    df_all.columns = cleaned_column_names
    # deleted column 'assessment' it has no data, no entries
    df_all = df_all.drop(columns=['assessment'])
    df_all = df_all.rename(columns={'location_details/_landmarks': 'location'})
    # converting the date to days only
    df_all['creation_date'] = pd.to_datetime(df_all['creation_date']).dt.date
    df_all['edit_date'] = pd.to_datetime(df_all['edit_date']).dt.date
    # setting creation date to the proper data format (to date time)
    df_all['creation_date'] = pd.to_datetime(
        df_all['creation_date'], infer_datetime_format=True)
    df_all['edit_date'] = pd.to_datetime(
        df_all['edit_date'], infer_datetime_format=True)
    # added line of code below
    #df_all.fillna("N_A", inplace = True)

    # Rename all the columns to snake_case convention
    df_all = df_all.rename(columns={'location_details_landmarks': 'location', 'type_of_event': 'event_type', 'who_was_involved': 'person_involved', 'other_who_was_involved': 'other_person_involved', 'what_was_the_situation': 'what_situation', 'other_what_was_the_situation': 'other_situation', 'medical/_health_concerns': 'medical_health_concerns', 'other_medical/_health_concerns': 'other_medical_health_concerns', 'problematic_social_behaviours': 'problematic_social_behavior', 'streetscape_&_public_realm': 'streetscape_public_realm', 'other_streetscape_&_public_realm': 'other_streetscape_public_realm',
                           'engagement_requested': 'engage_request', 'other_engagement_requested': 'other_engage_request', 'engagement_provided': 'engage_provided', 'channelling':'channelling', 'other_channelling':'other_channelling','report_completed_by': 'report_completed', 'assessment1': 'assessment', 'relevant_notes/_description_of_incident': 'notes_description', 'if_the_person_is_a_resident/_visitor/_person_with_ubn_have_you_o': 'previous_engagement', 'list_their_distinctive_characteristics/tags': 'yes_characteristics_tags', 'if_"_yes"_how_many_times_including_this_time': 'yes_number_times', 'x': 'x_longitude', 'y': 'y_latitude'})

    df_all = df_all.fillna('no_data')

    df_all = df_all.replace('N_A', 'no_data', regex=True)

    df_all = df_all.replace('N_A,', ',no_data', regex=True)

    df_all = df_all.replace(',N_A,', ',no_data', regex=True)

    df_all = df_all.replace('None', 'no_data')

    df_all["event_type"] = df_all["event_type"].str.replace(
        'Streetscape_Public_Realm', 'Streetscape', regex=False)

    df_all["creator"] = df_all["creator"].str.replace(
        'IvanOsorioAvila', 'Ivan Osorio Avila', regex=False)

    df_all["creator"] = df_all["creator"].str.replace(
        'carmen_12csi', 'Carmen Poon', regex=False)

    df_all["editor"] = df_all["editor"].str.replace(
        'IvanOsorioAvila', 'Ivan Osorio Avila', regex=False)

    df_all["editor"] = df_all["editor"].str.replace(
        'carmen_12csi', 'Carmen Poon', regex=False)

    # combine person_involved with other_person_involved column

    df_all['person_involved'] = df_all.person_involved.str.cat(
        df_all.other_person_involved, sep=",")
    df_all = df_all.drop(columns=['other_person_involved'])
    df_all["person_involved"] = df_all["person_involved"].str.replace(
        'other', 'no_data', regex=False)

    # combine what_situation with other_situation column

    df_all['what_situation'] = df_all.what_situation.str.cat(
        df_all.other_situation, sep=",")
    df_all = df_all.drop(columns=['other_situation'])
    df_all["what_situation"] = df_all["what_situation"].str.replace(
        'other', 'no_data', regex=False)

    # combine medical_health_concerns with other_medical_health_concerns column

    df_all['medical_health_concerns'] = df_all.medical_health_concerns.str.cat(
        df_all.other_medical_health_concerns, sep=",")
    df_all = df_all.drop(columns=['other_medical_health_concerns'])
    df_all["medical_health_concerns"] = df_all["medical_health_concerns"].str.replace(
        'other', 'no_data', regex=False)

    # combine streetscape_public_realm with other_streetscape_public_realm column

    df_all['streetscape_public_realm'] = df_all.streetscape_public_realm.str.cat(
        df_all.other_streetscape_public_realm, sep=",")
    df_all = df_all.drop(columns=['other_streetscape_public_realm'])
    df_all["streetscape_public_realm"] = df_all["streetscape_public_realm"].str.replace(
        'other', 'no_data', regex=False)

    # combine engage_request with other_engage_request column

    df_all['engage_request'] = df_all.engage_request.str.cat(
        df_all.other_engage_request, sep=",")
    df_all = df_all.drop(columns=['other_engage_request'])
    df_all["engage_request"] = df_all["engage_request"].str.replace(
        'other', 'no_data', regex=False)

    # combine channelling with other_channelling column
    df_all['channelling'] = df_all.channelling.str.cat(
        df_all.other_channelling, sep=",")
    df_all = df_all.drop(columns=['other_channelling'])
    df_all["channelling"] = df_all["channelling"].str.replace(
        'other', 'no_data', regex=False)

    # combine referrals with other_referrals column

    df_all['referrals'] = df_all.referrals.str.cat(
        df_all.other_referrals, sep=",")
    df_all = df_all.drop(columns=['other_referrals'])
    df_all["referrals"] = df_all["referrals"].str.replace(
        'other', 'no_data', regex=False)

    # combine engage_provided with other_engagement_provided column

    df_all['engage_provided'] = df_all.engage_provided.str.cat(
        df_all.other_engagement_provided, sep=",")
    df_all = df_all.drop(columns=['other_engagement_provided'])
    df_all["engage_provided"] = df_all["engage_provided"].str.replace(
        'other', 'no_data', regex=False)

    points = get_poi.get_events_geoenriched()
    points = points.drop(['index'], axis=1)
    #print(points.dtypes)
    coord = get_poi.get_places_geoenriched()
    coord = coord.drop(['index'], axis=1)
    #print(coord.dtypes)

    # spatial join checking our x and y to see if inside the polygon co-ordinates
    points_within = gpd.sjoin(points, coord.head(10))
    #points_within = gpd.sjoin(points, coord.head(10), op='within')
    points_within = points_within.rename(columns={'ObjectID': 'object_id'})
    #print(points_within.dtypes)

    # joining both dataframes based on object_id
    df_all = pd.merge(
        df_all, points_within[['object_id', 'name']], how='left', on=['object_id'])
    df_all = df_all.rename(columns={'name': 'hot_spot'})
    df_all.loc[df_all['hot_spot'].isna(), 'hot_spot'] = 'not in \'hotspot\''

    df_all['general_location'] = df_all['location']

    df_all = df_all[['index', 'object_id', 'global_id', 'creation_date', 'creator', 'edit_date', 'editor', 'location'] + ['general_location'] + ['event_type', 'person_involved', 'what_situation', 'medical_health_concerns', 'problematic_social_behavior',
                                                                                                                                                 'streetscape_public_realm', 'engage_request', 'engage_provided', 'channelling', 'referrals', 'report_completed', 'assessment', 'notes_description', 'previous_engagement', 'yes_characteristics_tags', 'yes_number_times', 'x_longitude', 'y_latitude', 'hot_spot']]

    # data cleaning to make a general location - so dashboard will have better more accurate information
    df_all['general_location'] = df_all['general_location'] = (
        df_all.general_location.str.lower())
    df_all["general_location"] = df_all["general_location"].str.replace(
        'forrest', 'forest', regex=False)
    df_all.loc[df_all['general_location'].str.contains(
        'shoppers'), 'general_location'] = 'shoppers drug mart'
    df_all.loc[df_all['general_location'].str.contains(
        'big al’s'), 'general_location'] = 'big al’s bar and grill'
    df_all.loc[df_all['general_location'].str.contains(
        'victory'), 'general_location'] = 'victory outreach church'
    df_all.loc[df_all['general_location'].str.contains(
        'alex'), 'general_location'] = 'the alex'
    df_all.loc[df_all['general_location'].str.contains(
        'bravo'), 'general_location'] = 'bravo restaurant'
    df_all.loc[df_all['general_location'].str.contains(
        'chicago’s pub'), 'general_location'] = 'chicago pub'
    df_all.loc[df_all['general_location'].str.contains(
        'chicken the way'), 'general_location'] = 'chicken on the way'
    df_all.loc[df_all['general_location'].str.contains(
        'mekong'), 'general_location'] = 'mekong vietnamese restaurant'
    df_all.loc[df_all['general_location'].str.contains(
        'osmows'), 'general_location'] = 'osmows mediterranean cuisine'
    df_all.loc[df_all['general_location'].str.contains(
        'shawarma'), 'general_location'] = 'shawarma palace'
    df_all.loc[df_all['general_location'].str.contains(
        'across from 4201 19ave'), 'general_location'] = 'across street from 4201 19ave'
    df_all.loc[df_all['general_location'].str.contains(
        'ba mien'), 'general_location'] = 'ba mien quan vietnamese cafe'
    df_all.loc[df_all['general_location'].str.contains(
        'circle k'), 'general_location'] = 'circle k'
    df_all.loc[df_all['general_location'].str.contains(
        'forest lawn physiotherapy'), 'general_location'] = 'forest lawn physiotherapy'
    df_all.loc[df_all['general_location'].str.contains(
        'fuse'), 'general_location'] = 'fuse 33'
    df_all.loc[df_all['general_location'].str.contains(
        'kokonut kove'), 'general_location'] = 'kokonut kove'
    df_all.loc[df_all['general_location'].str.contains(
        'marsha allah'), 'general_location'] = 'mashaallah restaurant'
    df_all.loc[df_all['general_location'].str.contains(
        'mashaalah'), 'general_location'] = 'mashaallah restaurant'
    df_all.loc[df_all['general_location'].str.contains(
        'nature’s food in store'), 'general_location'] = 'nature’s food and spice'


    return df_all
def target_columns():
    target_columns = ['event_type', 'person_involved',
       'what_situation', 'medical_health_concerns', 'problematic_social_behavior',
       'streetscape_public_realm', 'engage_request', 'engage_provided',
       'channelling', 'referrals', 'report_completed', 'assessment',
       'notes_description', 'previous_engagement','hot_spot']
    return target_columns
def input_data():
    input_data = [
        {'label':'Event Type', 'value': "event_type"},
        {'label':'Person Involved', 'value': "person_involved"},
        {'label':'What Situation', 'value': "what_situation"},
        {'label':'Medical Health Concerns', 'value': "medical_health_concerns"},
        {'label':'Problematic Social Behavior', 'value': "problematic_social_behavior"},
        {'label':'Streetscape', 'value': "streetscape_public_realm"},
        {'label':'Engagement Request', 'value': "engage_request"},
        {'label':'Engagement Provided', 'value': "engage_provided"},
        {'label':'Channelling', 'value': "channelling"},
        {'label':'Referrals', 'value': "referrals"},
        {'label':'Report Completed', 'value': "report_completed"},
        {'label':'Assessment', 'value': "assessment"},
        {'label':'Notes Description', 'value': "notes_description"},
        {'label':'Previous Engagement', 'value': "previous_engagement"},
        {'label':'Hot Spot', 'value': "hot_spot"},
    ]
    return input_data

if __name__ == '__main__':
    df = preprocess_and_load_survey_df()
#    print(df)


#df.to_csv('df.csv')
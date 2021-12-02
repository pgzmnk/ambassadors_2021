import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from itertools import chain

import preprocess

from app import app
#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
#This the website where the theme is picked https://bootswatch.com/flatly/

df_preprocess = preprocess.preprocess_and_load_survey_df()
df_preprocess['count_events']=1
df_preprocess['creation_date'] = pd.to_datetime(df_preprocess['creation_date'])

def create_visual_1 (df,v_criteria):
    # return list from series of comma-separated strings
    def chainer(s):
        return list(chain.from_iterable(s.str.split(',')))

    # calculate lengths of splits
    lens = df[v_criteria].str.split(',').map(len)

    # create new dataframe, repeating or chaining as appropriate
    df_visual_1 = pd.DataFrame({'creation_date': np.repeat(df['creation_date'], lens),
                        'event_type': np.repeat(df['event_type'], lens),
                        'location': np.repeat(df['location'], lens),
                        'count_events': np.repeat(df['count_events'], lens),
                        'x_longitude': np.repeat(df['x_longitude'], lens),
                        'y_latitude': np.repeat(df['y_latitude'], lens),
                        v_criteria: chainer(df[v_criteria])})
    df_visual_1.reset_index(drop=True, inplace=True)
    # remove no_data
    index_names = df_visual_1[ (df_visual_1[v_criteria] == 'no_data')].index
    # drop these given row
    # indexes from dataFrame
    df_visual_1.drop(index_names, inplace = True)
    return df_visual_1

def create_visual_2 (df,v_criteria):
    """Transform df_visual_1
    """
    df_visual_2 = df[['creation_date',v_criteria,'count_events']]
    df_visual_2=df_visual_2.groupby(['creation_date',v_criteria]).count().reset_index()
    return df_visual_2

target_columns = preprocess.target_columns()
input_data = preprocess.input_data()

category_dict = {v_criteria: list(set(create_visual_1(df_preprocess,v_criteria)[v_criteria])) for v_criteria in target_columns}

layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.H1("Hot Spots on International Avenue", style={'textAlign':'left'})
        ], width={'size': 10})
    ]),



    dbc.Row([
        dbc.Col([
            html.H4("SELECT RANGE DATES:"),
            dcc.DatePickerSingle(
                id='my-date-picker-start',
                min_date_allowed=df_preprocess['creation_date'].min(),
                max_date_allowed=df_preprocess['creation_date'].max(),
                initial_visible_month=date(2021, 9, 14),
                date=date(2021, 9, 14)
            ),
            dcc.DatePickerSingle(
                id='my-date-picker-end',
                min_date_allowed=df_preprocess['creation_date'].min(),
                max_date_allowed=df_preprocess['creation_date'].max(),
                initial_visible_month=df_preprocess['creation_date'].max(),
                date=df_preprocess['creation_date'].max(),
            ),
        ])
    ]),


    dbc.Row(
        dbc.Col(html.Hr(style={'border': "3px solid gray"}),width=12)
    ),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                    dbc.CardBody([
                        html.H5("Hot Spots (commonly active areas) are indicated by different colored polygons in the map below")
                    ])
                ]), 
            html.Br(),
        ], width={'size': 12})
    ]),



    dbc.Row([
        dbc.Col([
            dbc.Card([
            dbc.CardBody([
                dcc.Graph(id="hotspot-map1", config={'displayModeBar': True})
            ])
        ])
        ], width=12)
    ]),
])

@app.callback(
    Output('hotspot-map1','figure'),
    Input('my-date-picker-start','date'),
    Input('my-date-picker-end','date'),
)
def update_graph(start_date, end_date):
    dff = df_preprocess[df_preprocess.creation_date.between(start_date, end_date)]

    df_hotspots = dff[dff['hot_spot'] != 'not in \'hotspot\'']
    
    all_points_map = go.Scattermapbox(
        lat=dff['y_latitude'],
        lon=dff['x_longitude'],
        name='All events',
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            opacity=0.8,
            color='blue'
        )
    )
    
    maps_list = [all_points_map]
    
    for hs_loc in df_hotspots['hot_spot'].unique():
        df_hotspot_local = df_hotspots[df_hotspots['hot_spot'] == hs_loc]
        
        # draw rectangle
        lats = list(df_hotspot_local['y_latitude'])
        lons = list(df_hotspot_local['x_longitude'])
        
        lat_min, lat_max = min(lats), max(lats)
        lon_min, lon_max = min(lons), max(lons)
        
        fig_temp = go.Scattermapbox(
            mode = "lines", fill = "toself",
            lat=[lat_min, lat_min, lat_max, lat_max, lat_min],
            lon=[lon_min, lon_max, lon_max, lon_min, lon_min],
            name=hs_loc
        )
        
        maps_list.append(fig_temp)

    fig = go.Figure(maps_list)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            center=go.layout.mapbox.Center(
                lat=dff['y_latitude'].mean(),
                lon=dff['x_longitude'].mean()
            ),
            zoom=14
        )
    )

    return fig

import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
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
            html.H1("Dashboard Q9", style={'textAlign':'center'})
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H4("Select range dates:"),
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
        ])
        ], width=12),
    ]),

    dbc.Row(
        dbc.Col(html.Hr(style={'border': "3px solid gray"}),width=12)
    ),
# SECTION: Visitors Interactions, Incidents, Emergencies
    dbc.Row([
        dbc.Row(children=[html.H2('Analysis of "Building Rapport" situations')]),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Count of 'Building_Rapport' situations"),
                            html.Div(id="building-rapport-count", children="", className='card-big-text')
                        ])
                    ])
                ], width=4),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Notes"),
                            html.H5(id='br-concluding-remarks', children="'Building Rapport' situations",
                                    style={'fontWeight':'bold'})
                        ])
                    ])
                ], width=12)
            ], className="mb-3")
        ], width=4),

        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id="br-map1", config={'displayModeBar': True}
                                      )
                        ])
                    ])
                ], width=12),
            ])
        ], width=8)
    ],className="mt-3", justify='center'),

    dbc.Row(
    dbc.Col(html.Hr(style={'border': "3px solid gray"}),width=12)
    ),

# SECTION: Link to main Page
    dbc.Row(
        dbc.Col(
            dcc.Link('Go to main page', href='/')
        )
    ),
    dbc.Row(
        dbc.Col(html.Hr(style={'border': "3px solid gray"}),width=12)
    ),

])

# Update Map ***********************************************************
@app.callback(
    Output('building-rapport-count','children'),
    Output('br-map1','figure'),
    Input('my-date-picker-start','date'),
    Input('my-date-picker-end','date'),
)
def update_graph(start_date, end_date):
    dff = df_preprocess[df_preprocess.creation_date.between(start_date, end_date)]
    dff = dff[dff['what_situation'].str.contains('Building_Rapport', regex=False)]

    total_records = dff.shape[0]
    totals = f'{str(total_records)}'
    
    fig2 = px.scatter_mapbox(dff, 
                            lat="y_latitude", lon="x_longitude", hover_name='event_type', 
                            color='event_type', hover_data=["event_type", "location"], zoom=14, height=350)
    fig2.update_layout(mapbox_style="open-street-map")
    fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return total_records, fig2

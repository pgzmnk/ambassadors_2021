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
# SECTION : DatePickers and Total Records
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
        ], width={'size': 6, 'offset': 0, 'order': 1}),
        # dbc.Col([
        #     dbc.Card([
        #         dbc.CardHeader(html.H3("TOTAL RECORDS")),
        #         dbc.CardBody([
        #             html.H3(id="total_records", children="", style={'fontWeight':'bold', 'textAlign':'center'})
        #         ])
        #         ], color="success", inverse=True)
        #     ], width={'size': 4, 'offset': 1, 'order': 2})
    ]),

    dbc.Row(
        dbc.Col(html.Hr(style={'border': "3px solid gray"}),width=12)
    ),

# SECTION: TYPE OF EVENTS
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                html.H2("Type of Events")
                ]),
            ]), 
            html.Br(),
        ], width={'size': 12})
    ]),
    dbc.Row([
         dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Emergency")),
                dbc.CardBody([
                    html.H3(id="emergency", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                ])
             ])
         ], width=3),
         dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Interaction")),
                dbc.CardBody([
                    html.H3(id="interaction", children="", style={'fontWeight':'bold','textAlign':'center'})
                ])
            ])
         ], width=3),
         dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Incident")),
                dbc.CardBody([
                    html.H3(id="incident", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                ])
            ])
         ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Streetscape")),
                dbc.CardBody([
                    html.H3(id="streetscape", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                ])
                ])
         ], width=3),
    ]),
   # html.Br(),
    html.Hr(), 
    dbc.Row([
         dbc.Col([
            dbc.Card([
                dbc.CardBody([
                   # dbc.CardHeader(html.H4("Type of Events Map")),
                    dcc.Graph(id="map2", config={'displayModeBar': True}),
                    dbc.CardFooter("Note: Total type of events is the same as total records in the database"),
                ])
            ])
         ], width=12)
     ]),
    dbc.Row(
    dbc.Col(html.Hr(style={'border': "3px solid gray"}),width=12)
    ),
    
# SECTION: CPS, EMS, FIRE
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                html.H2("Emergency Services", 
                #style={'textAlign':'center'}
                )
                ])
            ]),
            html.Br(),
        ], width={'size': 12})
    ]),
     dbc.Row([
         dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("CPS")),
                dbc.CardBody([
                    html.H3(id="cps", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                ])
            ])
         ], width=3),
         dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("EMS")),
                    dbc.CardBody([
                         html.H3(id="ems", children="", style={'fontWeight':'bold','textAlign':'center'})
                    ])
                ])
         ], width=3),
         dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("FIRE")),
                    dbc.CardBody([
                        html.H3(id="fire", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                    ])
                ])
         ], width=3),
     ]),
     html.Br(),
     dbc.Row([
         dbc.Col([
                dbc.Card([
                #    dbc.CardHeader(html.H4("Map: CPS, Fire, EMS")),
                    dbc.CardBody([
                        dcc.Graph(id="map", config={'displayModeBar': True}),
                    ]),
                    dbc.CardFooter("Note: CPS, FIRE and EMS are within person_involved category"),
                ])
         ], width=12)
     ]),
    dbc.Row(
    dbc.Col(html.Hr(style={'border': "3px solid gray"}),width=12)
    ), 

], fluid=True, 
#style={'backgroundColor':'lightgrey'}
)

# Update Map ***********************************************************
@app.callback(
    Output('map','figure'),
    Output('cps','children'),
    Output('ems','children'),
    Output('fire','children'),
    Output('emergency','children'),
    Output('interaction','children'),
    Output('streetscape','children'),
    Output('incident','children'),
    # Output('total_records','children'),
    Output('map2','figure'),
    Input('my-date-picker-start','date'),
    Input('my-date-picker-end','date'),
)
def update_graph(start_date, end_date):
    dff=df_preprocess[df_preprocess.creation_date.between(start_date, end_date)]
    df_visual_1 = create_visual_1(dff,'person_involved')

    mask = df_visual_1['person_involved'].isin(['CPS','Fire','EMS'])
    fig = px.scatter_mapbox((df_visual_1)[mask], 
                            lat="y_latitude", lon="x_longitude", hover_name='person_involved', 
                            color='person_involved', hover_data=["event_type", "location"], zoom=14, height=300)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_traces(marker_size=10)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    cps_count = df_visual_1['person_involved'].value_counts()['CPS']
    cps = f'{str(cps_count)}'

    ems_count = df_visual_1['person_involved'].value_counts()['EMS']
    ems = f'{str(ems_count)}'

    fire_count = df_visual_1['person_involved'].value_counts()['Fire']
    fire = f'{str(fire_count)}'
  
    emergency_count = dff['event_type'].value_counts()['Emergency']
    emergency = f'{str(emergency_count)}'

    interaction_count = dff['event_type'].value_counts()['Interaction']
    interaction = f'{str(interaction_count)}'

    streetscape_count = dff['event_type'].value_counts()['Streetscape_Report']
    streetscape = f'{str(streetscape_count)}'

    incident_count = dff['event_type'].value_counts()['Incident']
    incident = f'{str(incident_count)}'

    # total_records = dff.shape[0]
    # totals = f'{str(total_records)}'
    
    mask2 = dff['event_type'].isin(['Emergency','Incident','Interaction','Streetscape_Report'])
    fig2 = px.scatter_mapbox(dff[mask2], 
                            lat="y_latitude", lon="x_longitude", hover_name='event_type', 
                            color='event_type', hover_data=["event_type", "location"], zoom=14, height=350)
    fig2.update_layout(mapbox_style="open-street-map")
    fig2.update_traces(marker_size=10)
    fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig, cps, ems, fire, emergency, interaction, streetscape, incident, fig2




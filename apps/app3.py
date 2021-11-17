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

target_columns = ['event_type', 'person_involved',
       'what_situation', 'medical_health_concerns', 'problem_social_behavior',
       'streetscape_public_realm', 'engage_request', 'engage_provided',
       'channeling', 'referrals', 'report_completed', 'assessment',
       'notes_description', 'previous_engagement','hot_spot']

input_data = [
        {'label':'Event Type', 'value': "event_type"},
        {'label':'Person Involved', 'value': "person_involved"},
        {'label':'What Situation', 'value': "what_situation"},
        {'label':'Medical Health Concens', 'value': "medical_health_concerns"},
        {'label':'Problem Social Behavior', 'value': "problem_social_behavior"},
        {'label':'Streetscape', 'value': "streetscape_public_realm"},
        {'label':'Engagement Request', 'value': "engage_request"},
        {'label':'Engagement Provided', 'value': "engage_provided"},
        {'label':'Channeling', 'value': "channeling"},
        {'label':'Referrals', 'value': "referrals"},
        {'label':'Report Completed', 'value': "report_completed"},
        {'label':'Assessment', 'value': "assessment"},
        {'label':'Notes Description', 'value': "notes_description"},
        {'label':'Previous Engagement', 'value': "previous_engagement"},
        {'label':'Hot Spot', 'value': "hot_spot"},
    ]

category_dict = {v_criteria: list(set(create_visual_1(df_preprocess,v_criteria)[v_criteria])) for v_criteria in target_columns}

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Emergency Services and Events", 
            #style={'textAlign':'center'}
            )
        ], width={'size': 10})
    ]),
    
    dbc.Row([
        dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H3("Select range dates:"),
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
# SECTION: CPS, EMS, FIRE
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2("CPS"),
                            html.H3(id="cps", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                        ])
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2("EMS"),
                            html.H3(id="ems", children="", style={'fontWeight':'bold','textAlign':'center'})
                        ])
                    ])
                ], width=4),

                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2("FIRE"),
                            html.H3(id="fire", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                        ])
                    ])
                ], width=4),
            ], 
            #className="mb-3"
            ),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Notes"),
                            html.H5(id='concluding-remarks', children="CPS, FIRE and EMS are within person_involved category",
                                    style={'fontWeight':'bold', 'textAlign':'center'})
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
                            html.P("Map CPS, Fire, EMS"),
                            dcc.Graph(id="map", config={'displayModeBar': True}
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

# SECTION: TYPE OF EVENTS
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2("Emergency"),
                            html.H3(id="emergency", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2("Interaction"),
                            html.H3(id="interaction", children="", style={'fontWeight':'bold','textAlign':'center'})
                        ])
                    ])
                ], width=6),

            ], 
            #className="mb-3"
            ),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2("Streetscape"),
                            html.H3(id="streetscape", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2("Incident"),
                            html.H3(id="incident", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                        ])
                    ])
                ], width=6),
            ], ),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2("Total Records"),
                            html.H3(id="total_records", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                        ])
                    ])
                ], width=6),

                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Notes:"),
                            html.H5(id='notes_type_events', children="Total type of events is the same as total records in the database",
                                    style={'fontWeight':'bold', 'textAlign':'center'})
                        ])
                    ])
                ], width=7)

            ], className="mb-3")
        ], width=4),

        dbc.Col([
            dbc.Row([
                    dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.P("Type of Events Map"),
                            dcc.Graph(id="map2", config={'displayModeBar': True}
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
    Output('total_records','children'),
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
                            color='person_involved', hover_data=["event_type", "location"], zoom=14, height=350)
    fig.update_layout(mapbox_style="open-street-map")
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

    total_records = dff.shape[0]
    totals = f'{str(total_records)}'
    
    mask2 = dff['event_type'].isin(['Emergency','Incident','Interaction','Streetscape_Report'])
    fig2 = px.scatter_mapbox(dff[mask2], 
                            lat="y_latitude", lon="x_longitude", hover_name='event_type', 
                            color='event_type', hover_data=["event_type", "location"], zoom=14, height=350)
    fig2.update_layout(mapbox_style="open-street-map")
    fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig, cps, ems, fire, emergency, interaction, streetscape, incident, totals, fig2




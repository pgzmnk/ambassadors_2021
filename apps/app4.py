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
                        'engage_provided': np.repeat(df['engage_provided'], lens),
                        'general_location': np.repeat(df['general_location'], lens),
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
       'notes_description', 'previous_engagement','hot_spot','general_location']

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
        {'label':'General Location', 'value': "general_location"},
    ]

category_dict = {v_criteria: list(set(create_visual_1(df_preprocess,v_criteria)[v_criteria])) for v_criteria in target_columns}

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Engagement Provided", style={'textAlign':'center'})
        ], width={'size': 10})
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
# SECTION: Wellness_Check, Emergency_Services_Channeling, Provided_Naloxone_Kit, Provided_Information
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Wellness Check"),
                            html.H2(id="Wellness_Check", children="", style={'fontWeight':'bold','textAlign':'center'})
                        ])
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Emergency Services Channeling"),
                            html.H2(id="Emergency_Services_Channeling", children="", style={'fontWeight':'bold','textAlign':'center'})
                        ])
                    ])
                ], width=4),

                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Provided Naloxone Kit"),
                            html.H2(id="Provided_Naloxone_Kit", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                        ])
                    ])
                ], width=4),

                dbc.Col([
                dbc.Card([
                        dbc.CardBody([
                            html.H5("Provided Information"),
                            html.H2(id="Provided_Information", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                        ])
                    ])
                ], width=4),


            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Notes"),
                            html.H5(id='concluding-remarks', children="Engagement Provided plotted on map sorted by color",
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
                            html.P("Engagement Provided is Wellness Checks, Emergency Channeling, Providing Naloxone Kits & Information"),
                            dcc.Graph(id="map_app4", config={'displayModeBar': True}
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
], fluid=True, style={'backgroundColor':'3px solid gray'})

# Update Map ***********************************************************
@app.callback(
    Output('map_app4','figure'),
    Output('Wellness_Check','children'),
    Output('Emergency_Services_Channeling','children'),
    Output('Provided_Naloxone_Kit','children'),
    Output('Provided_Information','children'),
    Input('my-date-picker-start','date'),
    Input('my-date-picker-end','date'),
)
def update_graph(start_date, end_date):
    dff=df_preprocess[df_preprocess.creation_date.between(start_date, end_date)]
    df_visual_1 = create_visual_1(dff,'engage_provided')

    mask = df_visual_1['engage_provided'].isin(['Wellness_Check','Emergency_Services_Channeling','Provided_Naloxone_Kit', 'Provided_Information'])
    fig = px.scatter_mapbox((df_visual_1)[mask], 
                            lat="y_latitude", lon="x_longitude", hover_name='engage_provided', 
                            color='engage_provided', hover_data=["event_type", "location"], zoom=14, height=350)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    wc_count = df_visual_1['engage_provided'].value_counts()['Wellness_Check']
    wc = f'{str(wc_count)}'

    esc_count = df_visual_1['engage_provided'].value_counts()['Emergency_Services_Channeling']
    esc = f'{str(esc_count)}'

    nal_count = df_visual_1['engage_provided'].value_counts()['Provided_Naloxone_Kit']
    nal = f'{str(nal_count)}'
  
    pi_count = df_visual_1['engage_provided'].value_counts()['Provided_Information']
    pi = f'{str(pi_count)}'

    total_records = dff.shape[0]
    totals = f'{str(total_records)}'
    
    return fig, wc, esc, nal, pi



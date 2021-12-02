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

target_columns = preprocess.target_columns()
input_data = preprocess.input_data()

category_dict = {v_criteria: list(set(create_visual_1(df_preprocess,v_criteria)[v_criteria])) for v_criteria in target_columns}

layout = dbc.Container([
     dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2("Engagement Provided")
                ])
            ]), 
            html.Br(),
        ], width={'size': 12})
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
        ], width={'size': 6, 'offset': 0, 'order': 1}),
    ]),
    dbc.Row(
    dbc.Col(html.Hr(style={'border': "3px solid gray"}),width=12)
    ),

 # SECTION: Wellness_Check, Emergency_Services_Channelling, Provided_Naloxone_Kit, Provided_Information
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Wellness Check")),
                dbc.CardBody([
                    html.H3(id="Wellness_Check", children="", style={'fontWeight':'bold', 'textAlign':'center'})
                ])
            ])
        ], width=3),
        dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Emergency Services Channelling")),
                    dbc.CardBody([
                         html.H3(id="Emergency_Services_Channelling", children="", style={'fontWeight':'bold','textAlign':'center'})
                    ])
                ])
        ], width=3),
        dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Provided Naloxone Kit")),
                    dbc.CardBody([
                         html.H3(id="Provided_Naloxone_Kit", children="", style={'fontWeight':'bold','textAlign':'center'})
                    ])
                ])
         ], width=3),
        dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Provided Information")),
                    dbc.CardBody([
                         html.H3(id="Provided_Information", children="", style={'fontWeight':'bold','textAlign':'center'})
                    ])
                ])
         ], width=3),
     ]),
    html.Br(),
    dbc.Row([
         dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id="map_app4", config={'displayModeBar': True}),
                    ]),
                    dbc.CardFooter("Note: Engagement Provided is Wellness Checks, Emergency Channelling, Providing Naloxone Kits & Information"),
                ])
         ], width=12)
     ]),
    dbc.Row(
    dbc.Col(html.Hr(style={'border': "3px solid gray"}),width=12)
    ),  

], fluid=True,
)

# Update Map ***********************************************************
@app.callback(
    Output('map_app4','figure'),
    Output('Wellness_Check','children'),
    Output('Emergency_Services_Channelling','children'),
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



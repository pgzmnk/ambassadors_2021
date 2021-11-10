import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import folium
from mapclassify import classify
import plotly.graph_objects as go
from itertools import chain

import preprocess


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
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

app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            html.H2( id='title_header', 
            className='text-center text-primary, mb-3'))),
    # Multiple-value dropdown
    dbc.Row([
        dbc.Col([
            html.H4('Select a category to evaluate:', className='text_center', style={'color':'blue','fontSize':'20'}),
            dcc.Dropdown(
                id='first-dropdown',
                options = input_data,
                multi=False,
                value = input_data[1]['value'],
                ),
        ], width={'size': 5, 'offset': 0, 'order': 1}),
    ]),
 
    dbc.Row([
        dbc.Col([
        dcc.Graph(id="sunburst", 
                style={'height':500}), 
        html.Hr()],
        width={'size': 7, 'offset': 0, 'order': 2}),
        
        dbc.Col([
        dcc.Graph(id='Histogram',
                style={'height':500}),  
        html.Hr(),
        ],width={'size': 5, 'offset': 0, 'order': 1})
    ]),
    dbc.Row([
        dbc.Col([
        dcc.Dropdown(
            id = 'second-dropdown',
            multi=True,
            ), 
        html.Hr()      
        ],width={'size': 12, 'offset': 0, 'order': 1}),
    ]),
    dbc.Row([
            dbc.Col([
            dcc.Graph(id="map", 
                    style={'height':350}), 
            html.Hr()],
            width={'size': 10, 'offset': 0, 'order': 1}),
    ]),
    dbc.Row([
        dbc.Col([
        dcc.Graph(id="bar-chart", 
                style={'height':400}), 
        html.Hr()],
        width={'size': 7, 'offset': 0, 'order': 1}),

        dbc.Col([
        dcc.Graph(id="table", 
                style={'height':400}), 
        html.Hr()],
        width={'size': 5, 'offset': 0, 'order': 2})
    ])        
])

@app.callback(
    Output('second-dropdown', 'options'),
    Output('title_header','children'),
    Input('first-dropdown', 'value')
)
def first_dropdown(first_dropdown_name):

    return [{'label': i, 'value': i} for i in category_dict[first_dropdown_name]], f'Values selected {str(first_dropdown_name)}'

@app.callback(
    dash.dependencies.Output('bar-chart','figure'),
    dash.dependencies.Output('map','figure'),
    dash.dependencies.Output('Histogram','figure'),
    dash.dependencies.Output('sunburst','figure'),
    dash.dependencies.Output('table','figure'),
    dash.dependencies.Input('first-dropdown','value'),
    dash.dependencies.Input('second-dropdown','value')
)

def update_line_chart(first_dropdown_name, second_dropdown_name):
    df_visual_1 = create_visual_1(df_preprocess,first_dropdown_name)
    df_visual_2 = create_visual_2(df_visual_1,first_dropdown_name)

    mask = df_visual_2[first_dropdown_name].isin(second_dropdown_name)
    fig = px.bar(create_visual_2(df_visual_1,first_dropdown_name)[mask], 
    x="creation_date", 
    y="count_events", 
    color=first_dropdown_name, title=" per day")
    fig.update_layout(margin={"r":0,"t":20,"l":0,"b":0})

    mask2 = df_visual_1[first_dropdown_name].isin(second_dropdown_name)
    fig2 = px.scatter_mapbox((df_visual_1)[mask2], 
                            lat="y_latitude", lon="x_longitude", hover_name=first_dropdown_name, 
                            color=first_dropdown_name, hover_data=["event_type", "location"], zoom=14, height=350)
    fig2.update_layout(mapbox_style="open-street-map")
    fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    fig3 = px.histogram(df_visual_1, y=first_dropdown_name)
    fig3.update_layout(margin={"r":10,"t":20,"l":0,"b":0})

    fig4 = px.sunburst(df_visual_1, path=[first_dropdown_name,'location'], values='count_events')
    fig4.update_layout(margin={"r":0,"t":30,"l":0,"b":30})

    fig5 = go.Figure(data=[go.Table(
        header=dict(values=[second_dropdown_name,'location', 'Type of Event'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df_visual_1[mask2][first_dropdown_name], df_visual_1[mask2].location, df_visual_1[mask2].event_type],
                   fill_color='lavender',
                   align='left')) ])
    fig5.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    return fig, fig2, fig3, fig4, fig5

# These two lines make the app run live when I call it with `python plotly_dropdown.py` on the terminal.
if __name__ == '__main__':
    app.run_server(debug=True)








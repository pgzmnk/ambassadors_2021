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
    dbc.Row(
        dbc.Col(
            html.H1( id='title_header_app2', 
            #className='text-center text-primary, mb-3'
            ))),
    # Multiple-value dropdown
    dbc.Row([
        dbc.Col([
            html.H3('Select a category to evaluate:', className='text_center', ),
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
                style={'height':500, 'color': 'blue', 'fontSize': 20}), 
        html.Hr()],
        width={'size': 7, 'offset': 0, 'order': 2}),
        
        dbc.Col([
        dcc.Graph(id='Histogram_app2',
                style={'height':500, 'color': 'blue', 'fontSize': 20}),  
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
            dcc.Graph(id="map_app2", 
                    #style={'height':350, 'color': 'blue', 'fontSize': 20}
                    ), 
            html.Hr()],
            width={'size': 11, 'offset': 0, 'order': 1}),
    ]),
    dbc.Row([
        dbc.Col([
        dcc.Graph(id="bar-chart", 
                style={'height':500, 'color': 'blue', 'fontSize': 20}), 
        html.Hr()],
        width={'size': 12, 'offset': 0, 'order': 1}),
    ]),
    dbc.Row([
        dbc.Col([
        dcc.Graph(id="table", 
                style={'height':1000, 'color': 'blue', 'fontSize': 20}), 
        html.Hr()],
        width={'size': 7, 'offset': 0, 'order': 2})
    ]),

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

@app.callback(
    dash.dependencies.Output('second-dropdown', 'options'),
    dash.dependencies.Output('title_header_app2','children'),
    [dash.dependencies.Input('first-dropdown', 'value')]
)
def first_dropdown(first_dropdown_name):
    options_second_dropdown = [{'label': i.replace("_"," "), 'value': i} for i in category_dict[first_dropdown_name]]
    return options_second_dropdown, f'Values selected {first_dropdown_name.replace("_"," ").title()}'

@app.callback(
    dash.dependencies.Output('bar-chart','figure'),
    dash.dependencies.Output('map_app2','figure'),
    dash.dependencies.Output('Histogram_app2','figure'),
    dash.dependencies.Output('sunburst','figure'),
    dash.dependencies.Output('table','figure'),
    [dash.dependencies.Input('first-dropdown','value')],
    [dash.dependencies.Input('second-dropdown','value')]
)

def update_line_chart(first_dropdown_name, second_dropdown_name):
    if second_dropdown_name is None:
        df_visual_1 = create_visual_1(df_preprocess,first_dropdown_name)
        df_visual_2 = create_visual_2(df_visual_1,first_dropdown_name)
        fig2 = px.scatter_mapbox((df_visual_1), 
                            lat="y_latitude", lon="x_longitude", 
                            color=first_dropdown_name, zoom=14, 
                            )
        fig2.update_layout(mapbox_style="open-street-map")
        fig2.update_traces(marker_size=10)

        fig3 = px.histogram(df_visual_1, y=first_dropdown_name)
        fig3.update_layout(margin={"r":10,"t":20,"l":0,"b":0})

        fig4 = px.sunburst(df_visual_1, path=[first_dropdown_name,'location'], values='count_events')
        fig4.update_layout(margin={"r":0,"t":10,"l":0,"b":10})

        fig = px.bar(df_visual_2, x="creation_date", y="count_events", 
        color=first_dropdown_name, title="Count per Day")
        fig.update_layout(
            font_family="Courier New",
            font_color="blue",
            title_font_family="Arial",
            xaxis_title="Creation Date",
            yaxis_title="Count",
            legend_title="Categories",
            title_font_color="purple",
            legend_title_font_color="purple"
        )
        fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        ))
        table_list = df_visual_1[first_dropdown_name].unique().tolist()
        fig5 = go.Figure(data=[go.Table(
        header=dict(values=[table_list,'location', 'Type of Event'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df_visual_1[first_dropdown_name], df_visual_1.location, df_visual_1.event_type],
                   fill_color='lavender',
                   align='left')) ])
        fig5.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        return fig, fig2, fig4, fig3, fig5
    else:
        df_visual_1 = create_visual_1(df_preprocess,first_dropdown_name)
        df_visual_2 = create_visual_2(df_visual_1,first_dropdown_name)

        mask = df_visual_2[first_dropdown_name].isin(second_dropdown_name)
        fig = px.bar(create_visual_2(df_visual_1,first_dropdown_name)[mask], 
        x="creation_date", 
        y="count_events", 
        color=first_dropdown_name, title="Count per Day")
        fig.update_layout(
            font_family="Courier New",
            font_color="blue",
            title_font_family="Arial",
            xaxis_title="Creation Date",
            yaxis_title="Count",
            legend_title="Categories",
            title_font_color="purple",
            legend_title_font_color="purple"
        )
        fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        ))
        mask2 = df_visual_1[first_dropdown_name].isin(second_dropdown_name)
        fig2 = px.scatter_mapbox((df_visual_1)[mask2], 
                                lat="y_latitude", lon="x_longitude", hover_name=first_dropdown_name, 
                                color=first_dropdown_name, hover_data=["event_type", "location"], zoom=14, height=350)
        fig2.update_layout(mapbox_style="open-street-map")
        fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig2.update_traces(marker_size=10)

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





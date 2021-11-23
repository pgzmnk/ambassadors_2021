import pandas as pd
import numpy as np
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from mapclassify import classify
import plotly.graph_objects as go
from itertools import chain
import geopandas as gpd

import preprocess
import get_poi

from app import app

#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
#This the website where the theme is picked https://bootswatch.com/flatly/

df_preprocess = preprocess.preprocess_and_load_survey_df()
df_preprocess['count_events']=1
df_preprocess['creation_date'] = pd.to_datetime(df_preprocess['creation_date'])

df_places = get_poi.get_places_geoenriched()
df_places = gpd.GeoDataFrame(df_places, geometry='geometry')

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
            html.H1( id='title_header', 
           # className='text-center text-primary, mb-3'
           )
            )),
    # Multiple-value dropdown
    dbc.Row([
        dbc.Col([
            html.H3('Select a category to evaluate:', className='text_center',
            # style={'color':'blue','fontSize':'50'}
             ),
            dcc.Dropdown(
                id='first-dropdown',
                options = input_data,
                multi=False,
                value = input_data[1]['value'],
                ),
            html.Br(),
            html.Hr(),
        ], width={'size': 5, 'offset': 0, 'order': 1}),
    ]),
    dbc.Row([              
        dbc.Col([
        dcc.Graph(id='Histogram',figure={}, clickData=None, hoverData=None, 
                    config={
                      'staticPlot': False,     # True, False
                      'scrollZoom': True,      # True, False
                      'doubleClick': 'reset',  # 'reset', 'autosize' or 'reset+autosize', False
                      'showTips': False,       # True, False
                      'displayModeBar': True,  # True, False, 'hover'
                      'watermark': True,
                      # 'modeBarButtonsToRemove': ['pan2d','select2d'],
                        },
                style={'height':500, 'color': 'blue', 'fontSize': 20}, 
                ),  
        html.Hr(),
        ],width={'size': 5, 'offset': 0, 'order': 1}),
        dbc.Col([
        dcc.Graph(id="sunburst_app1", 
                style={'height':500, 'color': 'blue', 'fontSize': 20}), 
        html.Hr()],
        width={'size': 7, 'offset': 0, 'order': 2}),
    ]),
    dbc.Row([
            dbc.Col([
            html.H3('Interactive Map', className='text_center', 
            #style={'color':'blue','fontSize':'20'}
            ),
            dcc.Graph(id="map_app1",  
                    style={'height':500, 'color': 'blue', 'fontSize': 20}, 
                    ), 
            html.Hr()],
            width={'size': 12, 'offset': 0, 'order': 1}),
    ]),
    dbc.Row([
        dbc.Col([
        dcc.Graph(id="bar-chart_app1", 
                style={'height':500, 'color': 'blue', 'fontSize': 20}), 
        html.Hr()],
        width={'size': 12, 'offset': 0, 'order': 1}),
    ]),  
    dbc.Row([
        dbc.Col([
        dcc.Graph(id="table_app1", 
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
    dash.dependencies.Output('Histogram','figure'),
    dash.dependencies.Output('title_header','children'),
    [dash.dependencies.Input('first-dropdown', 'value')]
)
def first_dropdown(first_dropdown_name):
 #    options_second_dropdown = [{'label': i.replace("_"," "), 'value': i} for i in category_dict[first_dropdown_name]]
    df_visual_1 = create_visual_1(df_preprocess,first_dropdown_name)
    fig3 = px.histogram(df_visual_1, y=first_dropdown_name)
    fig3.update_layout(margin={"r":10,"t":50,"l":0,"b":0}, clickmode='event+select')

    return fig3, f'Values selected {first_dropdown_name.replace("_"," ").title()}'

@app.callback(
    dash.dependencies.Output('map_app1','figure'),
    dash.dependencies.Output('sunburst_app1','figure'),
    dash.dependencies.Output('bar-chart_app1','figure'), 
    dash.dependencies.Output('table_app1','figure'),   
    dash.dependencies.Input('first-dropdown','value'),
    dash.dependencies.Input('Histogram', 'hoverData'),
    dash.dependencies.Input('Histogram', 'clickData'),
    dash.dependencies.Input('Histogram', 'selectedData'),
    )
def update_map(first_dropdown_name, hoverInfo, clk_data, slct_data):

    if slct_data is None:
        df_visual_1 = create_visual_1(df_preprocess,first_dropdown_name)
        df_visual_2 = create_visual_2(df_visual_1,first_dropdown_name)

        fig_polygons = px.choropleth_mapbox(df_places,
                           geojson=df_places.geometry,
                           locations=df_places.index,
                           color=df_places.name,
                           center={"lat": 51.037830, "lon": -113.981670},
                           mapbox_style="open-street-map", 
                           opacity=0.8, 
                           zoom=14)
        fig2 = px.scatter_mapbox((df_visual_1), 
                            lat="y_latitude", lon="x_longitude", 
                            color=first_dropdown_name 
                            )
        fig2.update_traces(marker_size=10)
        fig_map = fig_polygons.add_traces(fig2.data)

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
        )  )
        table_list = df_visual_1[first_dropdown_name].unique().tolist()
        fig5 = go.Figure(data=[go.Table(
        header=dict(values=[table_list,'location', 'Type of Event'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df_visual_1[first_dropdown_name], df_visual_1.location, df_visual_1.event_type],
                   fill_color='lavender',
                   align='left')) ])
        fig5.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        return fig_map, fig4, fig, fig5
    else:
        #print(f'hover data: {hoverInfo}')
        # print(hov_data['points'][0]['customdata'][0])
        # print(f'click data: {clk_data}')
        #print(f'selected data: {slct_data}')

        df_visual_1 = create_visual_1(df_preprocess,first_dropdown_name)
        dfff=pd.DataFrame(slct_data['points'])
        list_y = dfff['y'].tolist()      

     #    hover = hoverInfo['points'][0]['y']
     #    df_visual_1 = df_visual_1[df_visual_1[first_dropdown_name]==hover]
        df_visual_1 = df_visual_1[df_visual_1[first_dropdown_name].isin(list_y)]
        df_visual_2 = create_visual_2(df_visual_1,first_dropdown_name)

        fig_polygons = px.choropleth_mapbox(df_places,
                           geojson=df_places.geometry,
                           locations=df_places.index,
                           color=df_places.name,
                           center={"lat": 51.037830, "lon": -113.981670},
                           mapbox_style="open-street-map",
                           opacity=0.8, 
                           zoom=14)
        fig2 = px.scatter_mapbox((df_visual_1), 
                            lat="y_latitude", lon="x_longitude", 
                            color=first_dropdown_name 
                            )
        fig2.update_traces(marker_size=10)
        fig_map = fig_polygons.add_traces(fig2.data)      

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
        table_list2 = df_visual_1[first_dropdown_name].unique().tolist()
        fig5 = go.Figure(data=[go.Table(
        header=dict(values=[table_list2,'location', 'Type of Event'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df_visual_1[first_dropdown_name], df_visual_1.location, df_visual_1.event_type],
                   fill_color='lavender',
                   align='left')) ])
        fig5.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        return fig_map, fig4, fig, fig5









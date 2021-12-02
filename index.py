from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app
from apps import app1, app2, app3, app4, app5, app6, app7, app8
from components import navigation


CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navigation.sidebar,
    navigation.navbar,
    html.Div(id="page-content", style=CONTENT_STYLE),
    html.Br(),
])

index_page = html.Div([
    html.Br(),
    html.H1(children='East Calgary Ambassadors', 
            #className='text-center text-primary',
            id='home-page-title'),
    dbc.Row(
    dbc.Col(html.Hr(style={'border': "3px solid #C88141"}),width=12),
    ),
    html.H4('WHO WE ARE'),
    dbc.Row(
    dbc.Col(html.Hr(style={'border': "3px solid #8C001A"}),width=12)
    ),
    html.P('The Ambassador Program is a joint effort of the International Avenue BRZ and 12 Communities Safety Initiative (12CSI).'),
    html.P('We are here to help businesses, residents and all people that live, work, and visit the communities along the avenue.'),
    html.Br(),
    dbc.Row(
    dbc.Col(html.Hr(style={'border': "3px solid #151B8D"}),width=12)
    ),
    html.H4('DASHBOARD OBJECTIVES'),  
    dbc.Row(
    dbc.Col(html.Hr(style={'border': "3px solid #254117"}),width=12)
    ),   
    html.P('To create a data-driven story to better understand and share the unique needs and opportunities of the community.'),
    html.Br(),
    dbc.Row(
    dbc.Col(html.Hr(style={'border': "3px solid yellow"}),width=12)
    ),  
    html.H4('HOW THIS DASHBOARD WORKS'),
    dbc.Row(
    dbc.Col(html.Hr(style={'border': "3px solid #461B7E"}),width=12)
    ),  
    html.P('1.a. Select category from the dropdown menu, then click on sub-categories from histogram chart'),
    html.P('1.b. Select category from the first dropdown menu, then select sub-categories from second dropdown menu'),
    html.P('2 through 7 select date ranges to display interactive maps and data results'),
    html.Br(),
    html.P('Click green update button on left side to load the latest data'), 
], style={'fontWeight':'bold', 'textAlign':'left'})


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/apps/app1':
        return app1.layout
    elif pathname == '/apps/app2':
        return app2.layout
    elif pathname == '/apps/app3':
        return app3.layout
    elif pathname == '/apps/app4':
        return app4.layout
    elif pathname == '/apps/app5':
        return app5.layout
    elif pathname == '/apps/app6':
        return app6.layout
    elif pathname == '/apps/app7':
        return app7.layout
    elif pathname == '/apps/app8':
        return app8.layout
    else:
        return index_page


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8000)
    
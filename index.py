import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from itertools import chain


from views.view1 import app as app1
from views.view2 import app as app2
import preprocess

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


index_page = html.Div([
    dcc.Link('Go to Page 1', href='/views/1'),
    html.Br(),
    dcc.Link('Go to Page 2', href='/views/2'),
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):


    if pathname == '/views/1':
        return app1.layout
    elif pathname == '/views/2':
        return app2.layout
    else:
        return index_page

if __name__ == '__main__':
    app.run_server(debug=True)

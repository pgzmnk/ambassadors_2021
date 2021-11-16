from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app

layout = html.Div([
    html.H3('Main Page'),
    dcc.Link('Go to App 1', href='/apps/app1'),
    html.Br(),
    dcc.Link('Go to App 2', href='/apps/app2')
])

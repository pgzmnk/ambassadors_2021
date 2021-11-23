import subprocess
import sys 

from app import app
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate


# Path to `update data` script 
SCRIPT_TO_EXECUTE = 'survey123_to_postgres.py'


# Style of sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}


# Sidebar
sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink('Home', href='/', active="exact"),
                dbc.NavLink('Page 1', href='/apps/app1', active="exact"),
                dbc.NavLink('Page 2', href='/apps/app2', active="exact"),
                dbc.NavLink('Page 3', href='/apps/app3', active="exact"),
                dbc.NavLink('Page 4', href='/apps/app4', active="exact"),
                dbc.NavLink('Page 5', href='/apps/app5', active="exact"),
                dbc.NavLink('Page 6', href='/apps/app6', active="exact"),
                dbc.NavLink('Page 7', href='/apps/app7', active="exact"),
                dbc.Button("Update dataset from Survey123'", color="success", id='the-button', className="me-1"),

            ],
            vertical=True,
            pills=True,
        ),
        html.Div(id='body-div', className='card'),
    ],
    style=SIDEBAR_STYLE,
)


# Top navigation bar
DASHBOARD_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=DASHBOARD_LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand("Navbar", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="https://plotly.com",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        ]
    ),
    color="dark",
    dark=True,
)

# Callback for `update data` button
@app.callback(
    Output(component_id='body-div', component_property='children'),
    Input(component_id='the-button', component_property='n_clicks')
)
def update_output(n_clicks):
    subprocess.run([sys.executable, SCRIPT_TO_EXECUTE])
    if n_clicks is None:
        raise PreventUpdate
    else:
        return "Updated."

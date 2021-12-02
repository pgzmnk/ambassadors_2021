import pandas as pd
import subprocess
import sys 

from app import app
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import preprocess

# Path to `update data` script 
SCRIPT_TO_EXECUTE = 'survey123_to_postgres.py'

df_preprocess = preprocess.preprocess_and_load_survey_df()
#df_preprocess['creation_date'] = pd.to_datetime(df_preprocess['creation_date'])

# Style of sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "margin-top": "80px"
}

total_records = df_preprocess.shape[0]
totals = f'{str(total_records)}'

last_date = df_preprocess['creation_date'].max()
last_date = pd.to_datetime(pd.Series(last_date))
last_date =last_date.dt.strftime('%B %d, %Y')

# Sidebar
sidebar = html.Div(
    [
       # html.Img(src='/assets/12csi.png'),
        html.Br(),
        dbc.Nav(
            [
                dbc.NavLink('Home', href='/', active="exact"),
                dbc.NavLink('1.a. Interactive Data', href='/apps/app1', active="exact"),
                dbc.NavLink('1.b. Interactive Data', href='/apps/app2', active="exact"),
                dbc.NavLink('2. Events and Emergency Services', href='/apps/app3', active="exact"),
                dbc.NavLink('3. Engagement Provided', href='/apps/app4', active="exact"),
                dbc.NavLink('4. Visitors - Type of Events', href='/apps/app5', active="exact"),
                dbc.NavLink('5. Calgary Police Intervention - Type of Events', href='/apps/app6', active="exact"),
                dbc.NavLink('6. Building Rapport', href='/apps/app7', active="exact"),
                dbc.NavLink('7. Hot Spots', href='/apps/app8', active="exact"),
                dbc.Button("Update dataset from Survey123'", color="success", id='the-button', className="me-1"),

            ],
            vertical=True,
            pills=True,
        ),
        html.Br(),
        
        dbc.Card([
                dbc.CardHeader(html.H5("TOTAL RECORDS")),
                dbc.CardBody([
                    html.H3(id="total_records", children=totals, style={'fontWeight':'bold', 'textAlign':'center'})
                ]), 
                dbc.CardFooter([
                    html.P('Last update:'), 
                    html.P(f'{last_date[0]}')
                ]),
                ], color="primary", inverse=True),
        html.Br(),
        html.Div(id='body-div', 
        ),

    ],
    style=SIDEBAR_STYLE,
)

# Top navigation bar
DASHBOARD_LOGO1 = "/assets/12csi.png"
DASHBOARD_LOGO2 = "/assets/INTL_AVE_17.png"
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=DASHBOARD_LOGO1, height="70px")),
                        dbc.Col(html.Img(src=DASHBOARD_LOGO2, height="70px")),
                        dbc.Col(dbc.NavbarBrand("East Calgary Ambassadors", className="ms-2")),
                    ],
                    #align="center",
                    className="g-0",
                ),
                href="/",
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


# Callback for Total Records




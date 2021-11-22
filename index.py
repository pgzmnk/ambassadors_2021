import subprocess
import sys 
from dash.exceptions import PreventUpdate

from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app
from apps import app1, app2, app3, app4, app5, app6, app7
from nav_bar import nav_bar

SCRIPT_TO_EXECUTE = 'survey123_to_postgres.py'

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    nav_bar,
    html.Div(id='page-content'),
    html.Br(),
    html.Button('Update dataset from Survey123', id='the-button', className='card'),
    html.Div(id='body-div', className='card')    
])

index_page = html.Div([
    html.Br(),
    html.H1( children='East Calgary Ambassadors', 
            #className='text-center text-primary',
            id='home-page-title'),
    html.H3('Menu', style={'font-size': '30px',  'textAlign':'center'}),
    dcc.Link('Page 1 - Analysis Dashboard with Interactive Graph', href='/apps/app1',
            className='home-links'),
    dcc.Link('Page 2 - Analysis Dashboard with Dropdown', href='/apps/app2',
            className='home-links'), 
    dcc.Link('Page 3 - CPS, EMS, Fire Involved', href='/apps/app3',
            className='home-links'),
    dcc.Link('Page 4 - Location and Channelling', href='/apps/app4',
            className='home-links'),
    dcc.Link('Page 5 - Visitors Interactions, Incidents and Emergencies', href='/apps/app5',
            className='home-links'),
    dcc.Link('Page 6 - Analysis of CPS situations', href='/apps/app6',
            className='home-links'),
    dcc.Link('Page 7 - "Building Rapport" situations', href='/apps/app7',
            className='home-links'),
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
    else:
        return index_page

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

if __name__ == '__main__':
    app.run_server(debug=True)
    
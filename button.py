import subprocess
import sys 

import dash
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

SCRIPT_TO_EXECUTE = 'run_on_button_click.py'

app.layout = html.Div([
    html.Button('Update dataset from Survey123', id='the-button'),
    html.Div(id='body-div')
])

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

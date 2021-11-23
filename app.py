import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template


load_figure_template("materia")



app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.MATERIA])
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])


server = app.server
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app
from apps import app1, app2, app3, app4, app5, app6, app7
from nav_bar import nav_bar


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    nav_bar,
    html.Div(id='page-content')
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


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8000)
    
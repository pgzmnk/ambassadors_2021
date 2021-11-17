from dash import dcc
from dash import html

nav_bar = html.Div([
    html.Img(src='/assets/12csi.png', style={'height': '100px', 'padding': '0 20px' }),
    dcc.Link('Home', href='/', className='nav-bar-link'),
    dcc.Link('Page 1', href='/apps/app1', className='nav-bar-link'),
    dcc.Link('Page 2', href='/apps/app2', className='nav-bar-link'),
    dcc.Link('Page 3', href='/apps/app3', className='nav-bar-link'),
    dcc.Link('Page 4', href='/apps/app4', className='nav-bar-link'),
    dcc.Link('Page 5', href='/apps/app5', className='nav-bar-link'),
    dcc.Link('Page 6', href='/apps/app6', className='nav-bar-link'),
    dcc.Link('Page 7', href='/apps/app7', className='nav-bar-link'),
], className='nav-bar-container')
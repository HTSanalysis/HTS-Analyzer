import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

from app import app
from src import index, dashboard_layout

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='data-store', storage_type='local'),
    html.Div(id='page-content'),
    dcc.Store(id='final-time-val', storage_type='local'),
])

server = app.server

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return index.create_app_layout()
    
    elif pathname == '/dashboard-visualization':
        return dashboard_layout.create_page(navbar=index.create_navbar(download_report=True))


if __name__ == '__main__':
    app.run_server()

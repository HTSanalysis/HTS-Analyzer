import dash
import dash_bootstrap_components as dbc


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 
                        dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, suppress_callback_exceptions=True,
                title="HTS Analyzer", external_stylesheets=external_stylesheets,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server




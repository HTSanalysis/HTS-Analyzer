import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from src import execution
from app import app


def create_navbar(download_report=False):
    if download_report:
        return dbc.NavbarSimple(
                children=[
                 dbc.NavItem(dbc.Button("Download Report", id="download-report", 
                                        style={"font-weight": "bold"}), 
                             style={"margin-top": "2%"})
              ],
                brand="Welcome to HTS Analyzer",
                brand_href="/",
                color="primary",
                dark=True,
            )
        
    return dbc.NavbarSimple(
                brand="Welcome to HTS Analyzer",
                brand_href="/",
                color="primary",
                dark=True,
            )


def create_upload_contents():
    return dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Upload file',
                                   style={"text-decoration":"underline"})
                        ]),
                        style={
                            'width': '80%',
                            'height': '68px',
                            'display': 'block',
                            'margin-left': 'auto',
                            'margin-right': 'auto',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center'
                        },
                        # Allow one file at a time
                        multiple=False,
                    )
    

def show_graph_button():
    return html.Div(
            [
                dbc.Button(id="show-graphs", children="Show graphs and tables", color="primary", block=True),
                dbc.Popover(
                    [
                        dbc.PopoverHeader("Information required"),
                        dbc.PopoverBody("You must select a final time to proceed"),
                    ],
                    id="popover",
                    is_open=False,
                    target="show-graphs",
                ),
            ]
        )
    
    

def alert_user():
    return dbc.Alert(id="alert-info",  style={"text-align": "center"})



def get_final_time():
    return html.Div(
               [html.H5(id="final-time-text", style={'display': 'inline', 'margin-right': '2%'}),
                dcc.RadioItems(
                   id='final_time',
                   labelStyle={'margin-right': '2%'},
                   style={'display': 'none'},
                   ) 
                   ], 
               style={'text-align': 'center', 'padding-bottom': '2%'}
            )



def create_app_layout():
    return html.Div(
                id="get-started",
                
                children= [create_navbar(),
                           html.Br(), 
                           create_upload_contents(),
                           html.Br(), 
                           alert_user(),
                           html.Br(), 
                           get_final_time(),
                           show_graph_button()]
         )





@app.callback(
    Output("alert-info", "children"),
    Output("alert-info", "color"),
    Output('data-store', 'data'),
    Output("final_time", "style"),
    Output("final_time", "options"),
    Output("final-time-text", "children"),
    Input('upload-data', "contents"), 
    Input('upload-data', "filename")
)
def alert_info(contents, filename):
    status="Something went wrong"
    color="danger"
    data=None
    style={'display': 'none'}
    options=[]
    children=[]
    
    if filename is None:
        status="No file uploaded"
        color="warning"
        return status, color, data, style, options, children
    
    elif  not filename.endswith("csv"):
        status="file is not compatible. Please check the sample csv file"
        return status, color, data, style, options, children
    
    elif filename.endswith('csv'):
        df = execution.get_data(contents, filename)
        status="file uploaded successfully!"
        color="success"
        data=df.to_dict('records')
        style={'display': 'inline', 'text-align': 'center', 'padding-bottom': '2%'}
        options=execution.get_final_time_options(df)
        children="Select a final time:"
 
        return status, color, data, style, options, children
    
    else:
        status="Something went wrong, we are sorry for the inconvience!"
        return status, color, data, style, options, children




@app.callback(Output('url', 'pathname'), 
              Output("popover", "is_open"),
              Output('final-time-val', 'data'),
              Input("final_time", "value"),
              Input("show-graphs", "n_clicks"),
              State("popover", "is_open"))
def check_point(final_time, _, is_open):
    url="/"
    btn_clicked = [p['prop_id'] for p in dash.callback_context.triggered][0]
    final_time_val={}
    
    # if the user selects the final time option
    if final_time and "show-graphs" in btn_clicked:
        url='/dashboard-visualization'
        final_time_val['final_time']=final_time
    
        return url, is_open, final_time_val
    
    # when the user fails to select the final time option
    elif final_time is None and "show-graphs" in btn_clicked:
        return dash.no_update, not is_open, final_time_val
    
    return dash.no_update, dash.no_update, final_time_val

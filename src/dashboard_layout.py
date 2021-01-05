import os
import pandas as pd
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app
from src import plotting, execution, pdf_generation


def generate_placeholder_for_graphs():
    return html.Div(
            [
                dbc.Row(dbc.Col(dcc.Graph(id="time_zero-plot", config={"showTips": True, "displaylogo": False}))),     
                dbc.Row(dbc.Col(dcc.Graph(id="final_time-plot", config={"showTips": True, "displaylogo": False}))),
                dbc.Row(dbc.Col(dcc.Graph(id="CV_time_zero", config={"showTips": True, "displaylogo": False}))),
                dbc.Row(dbc.Col(dcc.Graph(id="CV_final_time", config={"showTips": True, "displaylogo": False}))),
                dbc.Row(
                    [
                        dbc.Col(dcc.Graph(id="f-strip-plot", config={"showTips": True, "displaylogo": False})),
                        dbc.Col(dcc.Graph(id="f-box-plot", config={"showTips": True, "displaylogo": False})),
                    ]
                ),
                dbc.Row(dbc.Col(dcc.Graph(id="dual-flash-light", config={"showTips": True, "displaylogo": False}))),
                dbc.Row(dbc.Col(dcc.Graph(id="adjusted-f", config={"showTips": True, "displaylogo": False}))),
                dbc.Row(dbc.Col(dcc.Graph(id="activity-plot", config={"showTips": True, "displaylogo": False}))),
                dbc.Row(dbc.Col(dcc.Graph(id="potential-hits", config={"showTips": True, "displaylogo": False}))),

            ]
        )
    
    

def generate_placeholder_for_tables():
    return html.Div(
                 [
                     html.H3(id="table-calc-info", 
                             style={"text-align": "center",
                                    "margin-top": "2%"}), 
                     html.Br(),
                     dbc.Col(html.Div(id='stats-table', style={"margin-left": "5%", "margin-right": "5%"})),
                     
                     html.H3("Table of potential hits", 
                              style={"text-align": "center",
                                    "margin-top": "2%"}),
                     html.Br(),
                     dbc.Col(html.Div(id='table-df', style={"margin-left": "5%", "margin-right": "5%"})),
                              
                     
                     html.Br(),

                 ]
            )
    
    

def download_info():
    return dbc.Modal(
            [
                dbc.ModalHeader("Download Completed!"),
                dbc.ModalBody("Your report has been downloaded to the Downloads folder in a folder called analytics_report"),
            ],
            id="modal",
            fade=True
        )


def create_page(navbar):
    return dcc.Loading(type='graph', 
                       fullscreen=True, 
                       
                       children=[navbar,
                                 download_info(),
                                 generate_placeholder_for_tables(),
                                 generate_placeholder_for_graphs()
                        ])
 

@app.callback(Output("table-calc-info", "children"),
              Output('time_zero-plot', 'figure'), 
              Output("final_time-plot", "figure"),
              Output('CV_time_zero', 'figure'), 
              Output("CV_final_time", "figure"),
              Output('f-strip-plot', 'figure'), 
              Output("f-box-plot", "figure"),
              Output('dual-flash-light', 'figure'), 
              Output("adjusted-f", "figure"),
              Output('activity-plot', 'figure'), 
              Output("potential-hits", "figure"),
              Output("stats-table", "children"),
              Output("table-df", "children"),
              Input('data-store', 'data'),
              Input('final-time-val', 'data'))
def update_graphs_and_tables(data, final_time):
    df=pd.DataFrame.from_records(data)
    final_time=final_time['final_time']
    table_header= "Calculations are based on the time -> " + final_time
    fig1, fig2= plotting.plot_annotated_heatmaps(df=df, final_time=final_time)
    fig3, fig4 = plotting.plot_cv_analysis(df=df, final_time=final_time)
    fig5, fig6 = plotting.plot_distribution(df=df, final_time=final_time)
    fig7, fig8, fig9, fig10 = plotting.plot_activity_graphs(df=df)
    stats, table = plotting.show_z_analysis_info(df=df, final_time=final_time)
    
    return table_header, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, stats, table

    



@app.callback(
    Output("modal", "is_open"),
    Input('data-store', 'data'),
    Input('final-time-val', 'data'),
    Input("download-report", "n_clicks"), 
    State("modal", "is_open"),
)
def perfom_download_and_alert_user(data, final_time, download, is_open):
    df=pd.DataFrame.from_records(data)
    final_time=final_time['final_time']
    fig1, fig2= plotting.plot_annotated_heatmaps(df=df, final_time=final_time)
    fig3, fig4 = plotting.plot_cv_analysis(df=df, final_time=final_time)
    fig5, fig6 = plotting.plot_distribution(df=df, final_time=final_time)
    fig7, fig8, fig9, fig10 = plotting.plot_activity_graphs(df=df)
    
    if download:
        _, DF_temp, _= execution.perform_more_advanced_stuffs(df)
        pa, na, ps, ns, z, _ = execution.perform_z_analysis(df, final_time)
        pdf_generation.generate_pdf(fig1, fig2, fig3, fig4, fig5,
                                    fig6, fig7, fig8, fig9, fig10, 
                                    final_time=final_time, DF_temp=DF_temp, 
                                    pa=pa, na=na, ps=ps, ns=ns, z=z)
        return not is_open
    return is_open



import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import plotly.figure_factory as ff
import dash_table

from src import execution


def update_plot(fig, title, xaxis_title=None, yaxis_title=None, top_padding=0.92):
    
    title_text= "<b>" + title + "</b>"
    
    if xaxis_title is None and yaxis_title is None:
        fig.update_layout(template= "plotly",
                          title={
                            'text': title_text,
                            'y':top_padding,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'})
        
    elif xaxis_title is not None and yaxis_title is not None:
        fig.update_layout(template= "plotly",
                          title={
                            'text': title_text,
                            'y':top_padding,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
                          xaxis_title=xaxis_title, 
                          yaxis_title=yaxis_title)
        
    else:
        raise Exception("Something is wrong somewhere!")
        
    return fig




def plot_annotated_heatmaps(df, final_time, nearest_dp=1):
    DF_384_zero, DF_384_final = execution.generate_dfs_for_plots(df, final_time)
    
    fig1= ff.create_annotated_heatmap(DF_384_zero.values.round(nearest_dp)[::-1], 
                                      y=DF_384_zero.index.tolist()[::-1], 
                                      showscale=True)
    
    fig2= ff.create_annotated_heatmap(DF_384_final.values.round(nearest_dp)[::-1],
                                      y=DF_384_final.index.tolist()[::-1], 
                                      showscale=True)
    
    # Make text size smaller
    for i in range(len(fig1.layout.annotations)):
        fig1.layout.annotations[i].font.size = 5
        
    for i in range(len(fig2.layout.annotations)):
        fig2.layout.annotations[i].font.size = 5
    
    fig1 = update_plot(fig=fig1, 
                       title="Time Zero", 
                       top_padding=0.9)
    
    fig2 = update_plot(fig=fig2, 
                       title="Final Time", 
                       top_padding=0.9)
    
    fig1.update_xaxes(side="bottom")
    fig2.update_xaxes(side="bottom")
    
    return fig1, fig2





def plot_cv_analysis(df, final_time, nearest_dp=3):
    DF_384_zero, DF_384_final = execution.generate_dfs_for_plots(df, final_time)
    DF_CV_zero, DF_CV_final = execution.generate_dfs_for_cv_analysis(df, DF_384_zero, DF_384_final)

    fig1= ff.create_annotated_heatmap(DF_CV_zero.values.round(nearest_dp)[::-1], 
                                      y=DF_CV_zero.index.tolist()[::-1], 
                                      showscale=True)
    
    fig2= ff.create_annotated_heatmap(DF_CV_final.values.round(nearest_dp)[::-1],
                                      y=DF_CV_final.index.tolist()[::-1], 
                                      showscale=True)
    
    # Make text size smaller
    for i in range(len(fig1.layout.annotations)):
        fig1.layout.annotations[i].font.size = 7
        
    for i in range(len(fig2.layout.annotations)):
        fig2.layout.annotations[i].font.size = 7
    
    fig1 = update_plot(fig=fig1, 
                       title="CV @ Time Zero", 
                       top_padding=0.9)
    
    fig2 = update_plot(fig=fig2, 
                       title="CV @ Final Time", 
                       top_padding=0.9)
    
    fig1.update_xaxes(side="bottom")
    fig2.update_xaxes(side="bottom")
    
    return fig1, fig2





def plot_distribution(df, final_time):
    *_, df_plate  = execution.perform_z_analysis(df, final_time)
    fig1 = px.strip(df_plate, x="plate", y="Fluorescence", color='test', facet_col='time')
    fig2 = px.box(df_plate, x="plate", y="Fluorescence", color='test', facet_col='time')

    fig1 = update_plot(fig=fig1, 
                       title="Fluorescence change over time", 
                       top_padding=0.97)
    
    fig2 = update_plot(fig=fig2, 
                       title="Fluorescence change over time", 
                       top_padding=0.97)
    
    return fig1, fig2





def plot_activity_graphs(df):
    DF_flash, _, DF_96 = execution.perform_more_advanced_stuffs(df)
    
    # Dual flash-light plot 
    fig1 = go.Figure(data=go.Scatter(x=DF_flash['activity'],
                                     y=DF_flash['t_test'],
                                     mode='markers',
                                     marker_color=DF_flash['p_value'],
                                     marker=dict(
                                         color=DF_flash['p_value'],
                                         colorbar=dict(title="P-value")),
                                     text=DF_flash['well'])) 
    
    
    pt=DF_flash[DF_flash['well']=='WT'].iloc[0,2]
    pa=DF_flash[DF_flash['well']=='WT'].iloc[0,1]
    ps=pa+DF_flash[DF_flash['well']=='WT'].iloc[0,4]
    
    
    
    fig1 = update_plot(fig=fig1, 
                     title="Dual flash-light plot", 
                     xaxis_title="Activity % compare to EV", 
                     yaxis_title="log(t-test)", 
                     top_padding=0.9)
    
    fig1.add_hline(pt, line_color="green", line_dash="dot")
    fig1.add_vline(pa, line_color="red", line_dash="dot")
    
    DF_b=DF_96.groupby(['well']).mean().sort_values(by=['Flourecense'])
    pa2=DF_96[DF_96['well']=='WT'].groupby(['well']).mean().iloc[0,0]
    na=DF_96[DF_96['well']=='EV'].groupby(['well']).mean().iloc[0,0]


    # bar graph of adjusted flourecense
    fig2= px.bar(x=DF_96["well"], y=DF_96["Flourecense"], barmode="overlay")
    
    fig2 = update_plot(fig=fig2, 
                     title="Adjusted flourecense for each well", 
                     xaxis_title="Well", 
                     yaxis_title="Adjusted Fluorescence", 
                     top_padding=0.94)
    
    fig2.add_hline(pa2, line_color="red", line_dash="dot")
    fig2.add_hline(na, line_color="green", line_dash="dot")
    
    pa3=DF_flash[DF_flash['well']=='WT'].groupby(['well']).mean().iloc[0,0]
    na3=DF_flash[DF_flash['well']=='EV'].groupby(['well']).mean().iloc[0,0]

    # bar graph of activity for each well
    fig3= px.bar(x=DF_96["well"], y=DF_96["activity"], barmode="overlay")
    
    
    fig3 = update_plot(fig=fig3, 
                     title="Activity for each well", 
                     xaxis_title="Well", 
                     yaxis_title="Activity (%) vs EV", 
                     top_padding=0.94)

    fig3.add_hline(pa3, line_color="red", line_dash="dot")
    fig3.add_hline(na3, line_color="black", line_dash="dot")
    
    DF_a=DF_flash[(DF_flash['well']=='WT')|(DF_flash['activity']>=pa) & (DF_flash['p_value']<=0.1)]

    pa4 = DF_flash[DF_flash['well']=='WT'].groupby(['well']).mean().iloc[0,0]
    na4 = DF_flash[DF_flash['well']=='EV'].groupby(['well']).mean().iloc[0,0]
    
    # graph for potential hits
    fig4 = px.bar(DF_a, x="well", y="activity", text='activity', color='well')
    
    fig4.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig4 = update_plot(fig=fig4, 
                       title="Potential hits based on average and p-value", 
                       xaxis_title="Well", 
                       yaxis_title="Activity (%) vs EV", 
                       top_padding=0.95)
    
    fig4.add_hline(pa4, line_color="red", line_dash="dot")


    
    return fig1, fig2, fig3, fig4



def show_z_analysis_info(df, final_time):
    pa, na, ps, ns, z, _ = execution.perform_z_analysis(df, final_time) 
    _, DF_temp, _ = execution.perform_more_advanced_stuffs(df)
    
    variable_names= ["WT average", 
                    "EV average", 
                    "WT standard deviation", 
                    "EV standard deviation", 
                    "Z-prime for this plate"]
    
    values=[pa, na, ps, ns, z]
    
    stats_table=pd.DataFrame()
    stats_table['statistic']=variable_names
    stats_table['value']=values

    stats = dash_table.DataTable(
        data=stats_table.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in stats_table.columns],
        style_as_list_view=True,
        style_header={'backgroundColor': 'rgb(9, 104, 244)', 
                      'fontWeight': 'bold', 'color': 'white', 
                      'font-size': '1.5rem', 'font-family': ['Roboto', 'sans-serif']},
        style_cell={
            'color': 'black',
            'textAlign': 'center',
            'font-family': ['Roboto', 'sans-serif']
          },
        )
    
    table= dash_table.DataTable(
        data=DF_temp.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in DF_temp.columns],
        style_header={'backgroundColor': 'rgb(9, 104, 244)', 'color': 'white', 
                      'fontWeight': 'bold', 'font-size': '1.5rem',
                      'font-family': ['Roboto', 'sans-serif']},
        style_cell={
            'color': 'black',
            'textAlign': 'center',
            'font-family': ['Roboto', 'sans-serif']
          },
        )
    
    return stats, table












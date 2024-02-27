import pandas as pd
import dash
from dash import Dash, html, dash_table, dcc, callback
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objs as go 
from plotly.subplots import make_subplots
from statsmodels.tsa.statespace.sarimax import SARIMAX
from urllib.request import urlopen
import json

df = pd.read_csv('online_retail.csv')
rfm = pd.read_csv('processed_rfm_model.csv')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['Total_Sale']=df['Quantity']*df['UnitPrice']
df=df[df['Total_Sale']!=0]
df=df.merge(rfm[['CustomerID', 'Cluster']], on='CustomerID', how='left')

# # Customize the layout
# fig_trend.update_layout(
#     xaxis_title='Month',
#     yaxis_title='Total Revenue',
#     xaxis=dict(
#         tickangle=-45,
#         title_font=dict(size=14),
#         tickfont=dict(size=12)
#     ),
#     yaxis=dict(
#         title_font=dict(size=14),
#         tickfont=dict(size=12)
#     )
# )

# ts 
df1 = df
df_ts = df1[['InvoiceDate', 'Total_Sale']]
df_ts.set_index('InvoiceDate', inplace=True)
day_sales = df_ts['Total_Sale'].resample('D').sum()
day_diff_sales = day_sales.diff().dropna()

model = SARIMAX(day_diff_sales, order=(0,0,2), seasonal_order=(1,0,2,7)) 
model_fit = model.fit(disp=False)  
forecast = model_fit.forecast(steps=82)
forecast_df = pd.DataFrame(forecast)
forecast_df.rename(columns={'predicted_mean': 'Total_Sale'}, inplace=True)
df_ts = df_ts.combine_first(forecast_df)

monthly_sales = df_ts['Total_Sale'].resample('M').sum()
trend_fig = make_subplots(specs=[[{"secondary_y": False}]])
trend_fig.add_trace(     
    go.Bar(x=monthly_sales.index[:-3], 
           y=monthly_sales[:-3], 
           name='Monthly Sales'),     
    secondary_y=False, 
    )
trend_fig.add_trace(     
    go.Bar(         
        x=monthly_sales.index[-3:],          
        y=monthly_sales[-3:],        
        marker=dict(color='rgba(255, 0, 0, 0.5)'),
        name='Prediction'
        ))
trend_fig.add_trace(     
    go.Scatter(x=monthly_sales.index, y=monthly_sales, name='Sales Trend'),     
    secondary_y=False,      
    )
trend_fig.update_layout(
    title='Sales Trend',
    xaxis_title='Month',
    yaxis_title='Sales'
)
# pie
cluster_counts = df['Cluster'].value_counts().reset_index()
cluster_counts.columns = ['Cluster', 'count']
pie_fig = px.pie(cluster_counts, 
                            values='count', 
                            names='Cluster', 
                            title='Cluster Segmentation')

# map 
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

map_fig = px.choropleth_mapbox(
    data_frame = df,   
    geojson=counties, 
    locations='Country', color='Cluster',
    color_continuous_scale="Viridis",
    mapbox_style="carto-positron",
    zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
    opacity=0.5,
    labels={'Total_Sale':'Sales'}
    )

dash.register_page(__name__, path='/page-1') # '/' is home page

layout = html.Div(
    [
        dcc.Dropdown(
        id='country-selector',
        options=[{'label': country, 'value': country} for country in df['Country'].unique()],
        value=df['Country'].unique()[0]  
    ),
        # dbc.Row(
        #     [
        #         dbc.Col(
        #             [
        #                 dcc.Dropdown(options=df.continent.unique(),
        #                              id='cont-choice')
        #             ], xs=10, sm=10, md=8, lg=4, xl=4, xxl=4
        #         )
        #     ]
        # ),
        dcc.Graph(id='sales_trend_ts', figure=trend_fig),

        dbc.Row([
            dbc.Col([dcc.Graph(id='sales_map', figure=map_fig)]),
            dbc.Col([dcc.Graph(id='cluster_pie',figure=pie_fig)])            
        ])
    ]
)

@callback(
    [Output('sales_trend_ts', 'figure'),
     Output('cluster_pie', 'figure')],
    [Input('country-selector', 'value')]
)
def update_sales_trend(selected_country):
    filtered_df = df[df['Country'] == selected_country]
    df_ts = filtered_df[['InvoiceDate', 'Total_Sale']]
    df_ts.set_index('InvoiceDate', inplace=True)
    day_sales = df_ts['Total_Sale'].resample('D').sum()
    day_diff_sales = day_sales.diff().dropna()

    model = SARIMAX(day_diff_sales, order=(0,0,2), seasonal_order=(1,0,2,7)) 
    model_fit = model.fit(disp=False)  
    forecast = model_fit.forecast(steps=82)
    forecast_df = pd.DataFrame(forecast)
    forecast_df.rename(columns={'predicted_mean': 'Total_Sale'}, inplace=True)
    df_ts = df_ts.combine_first(forecast_df)

    monthly_sales = df_ts['Total_Sale'].resample('M').sum() 
    trend_fig = make_subplots(specs=[[{"secondary_y": False}]]) 
    trend_fig.add_trace(          
        go.Bar(x=monthly_sales.index[:-3],             
               y=monthly_sales[:-3],             
               name='Monthly Sales'),          
               secondary_y=False,      
               ) 
    trend_fig.add_trace(          
        go.Bar(                  
            x=monthly_sales.index[-3:],                   
            y=monthly_sales[-3:],                 
            marker=dict(color='rgba(255, 0, 0, 0.5)'),
            name='Prediction'     
            )) 
    trend_fig.add_trace(          
        go.Scatter(x=monthly_sales.index, y=monthly_sales, name='Sales Trend'),          
        secondary_y=False,           
        ) 
    trend_fig.update_layout(     
        title='Sales Trend',     
        xaxis_title='Month',     
        yaxis_title='Sales'
        )
    
    cluster_counts = filtered_df['Cluster'].value_counts().reset_index()
    cluster_counts.columns = ['Cluster', 'count']
    pie_fig=px.pie(cluster_counts, 
                            values='count', 
                            names='Cluster', 
                            title='Cluster Segmentation'
                              )
    return [trend_fig, pie_fig]

# @callback(
#    Output('sales_map', 'figure'),
#    [Input('cluster-slider', 'value')]
#)
#def update_sales_map(selected_cluster):
#    filtered_df = df[df['clusters'] == selected_cluster]
#    
#    map_fig = px.scatter_mapbox(filtered_df,
#                            lat="Lat",
#                            lon="Lon",
#                            size="Sales",
#                            color="clusters",
#                            size_max=15,
#                            zoom=10,
#                            mapbox_style="open-street-map")
    
#    return map_fig
import pandas as pd
import dash
from dash import Dash, html, dash_table, dcc, callback
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objs as go 
from plotly.subplots import make_subplots
from statsmodels.tsa.statespace.sarimax import SARIMAX

df = pd.read_csv('online_retail.csv')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['Total_Sale']=df['Quantity']*df['UnitPrice']
df=df[df['Total_Sale']!=0]


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
        marker=dict(color='rgba(255, 0, 0, 0.5)')
        ))
trend_fig.add_trace(     
    go.Scatter(x=monthly_sales.index, y=monthly_sales, name='Sales Trend'),     
    secondary_y=False,      
    )
trend_fig.update_layout(
    title='Sales Trend',
    xaxis_title='Month',
    yaxis_title='Sales',
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
        dcc.Graph(id='sales_trend_ts', figure=trend_fig)
    ]
)

@callback(
    [Output('sales_trend_ts', 'figure')],
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
            marker=dict(color='rgba(255, 0, 0, 0.5)')     
            )) 
    trend_fig.add_trace(          
        go.Scatter(x=monthly_sales.index, y=monthly_sales, name='Sales Trend'),          
        secondary_y=False,           
        ) 
    trend_fig.update_layout(     
        title='Sales Trend',     
        xaxis_title='Month',     
        yaxis_title='Sales', 
        )
    return [trend_fig]
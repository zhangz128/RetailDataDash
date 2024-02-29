import pandas as pd
import dash
from dash import Dash, html, dash_table, dcc, callback
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objs as go 
from plotly.subplots import make_subplots
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pycountry

df = pd.read_csv('online_retail.csv')
rfm = pd.read_csv('processed_rfm_model.csv')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['Total_Sale']=df['Quantity']*df['UnitPrice']
df=df.merge(rfm[['CustomerID', 'Cluster']], on='CustomerID', how='left')
df=df[df['Total_Sale']!=0]
df=df[df['Total_Sale']>=0]

df['Year'] = df['InvoiceDate'].dt.year
years = df['Year'].unique()
years.sort()


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

monthly_sales = df_ts['Total_Sale'].resample('ME').sum()
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

#bubble map
def get_iso_alpha_3(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except LookupError:
        return None
    
df['iso_alpha'] = df['Country'].apply(get_iso_alpha_3)

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

# country_sales = df.groupby('Country')['Total_Sale'].sum().reset_index()

# country_sales['iso_alpha'] = country_sales['Country'].apply(get_iso_alpha_3)


# bubble_fig = px.choropleth(country_sales, locations='iso_alpha', 
#                      hover_name='Country', projection='natural earth',
#                      title='Heatmap of costomers segmentation')

dash.register_page(__name__, path='/page-1', external_stylesheets=external_stylesheets) # '/' is home page

cluster_mapping = {
    i: cluster for i, cluster in enumerate(
        ['lost customer', 'loyal customer', 'new customer', 'potential loyal customer'])}

layout = html.Div([
    dcc.Dropdown(
        id='country-selector',
        options=[{'label': country, 'value': country} for country in df['Country'].unique()],
        value=df['Country'].unique()[0]  
    ),
    dcc.Graph(id='sales_trend_ts', figure=trend_fig),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='map'),

            dcc.Slider(
                id='cluster-slider',
                min=0,
                max=len(cluster_mapping) - 1,  # Since index starts at 0
                value=0,  # Default value
                marks={i: name for i, name in cluster_mapping.items()},
                step=1  # Force selection of only integer positions
            )], width=8),
            
        dbc.Col([
            dcc.Graph(id='cluster_pie', figure=pie_fig)
        ], width=4)
    ])
])

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

    monthly_sales = df_ts['Total_Sale'].resample('ME').sum() 
    trend_fig = make_subplots(specs=[[{"secondary_y": False}]]) 
    trend_fig.add_trace(          
        go.Bar(x=monthly_sales.index[:-3],             
               y=monthly_sales[:-3],
               marker=dict(color='rgba(27, 171, 210, 0.7)'),             
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
        go.Scatter(x=monthly_sales.index, y=monthly_sales, line=dict(color='rgba(0,143,140,1)')),          
        secondary_y=False,           
        ) 
    
    trend_fig.update_layout(    
        title={
            'text': f'Sales Trend for {selected_country}',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                #'family': 'Arial, sans-serif',
                'size':24,
                'color': 'black'
            }
        },     
        xaxis_title='Month',     
        yaxis_title='Sales',
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(237,249,253,1)',
        )
    
    cluster_counts = filtered_df['Cluster'].value_counts().reset_index()
    cluster_counts.columns = ['Cluster', 'count']
    custom_colors = ['#AAE5F4','#4991BA','#FFC357','#FFF7C5']
    pie_fig=px.pie(cluster_counts, 
                   values='count', 
                   names='Cluster',
                   color_discrete_sequence=custom_colors                  
                   )
    
    pie_fig.update_layout(
        title={
            'text': f'Cluster Segmentation <br> for {selected_country}',
            'y':0.9,
            'x':0.43,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                #'family': 'Arial, sans-serif',
                'size':20,
                'color': 'black'
            }
        }
    )
    return [trend_fig, pie_fig]

@callback(
    Output('map', 'figure'),
    [Input('cluster-slider', 'value')]
)
def update_map(selected_segment):
    cluster_name = cluster_mapping[selected_segment]
    # Filter your dataset based on the selected segment
    # This assumes you have a way to filter your `df` based on the segmentation, which isn't shown here
    filtered_df = df[df['Cluster'] == cluster_name]  # Example filter, adjust to your dataframe
    
    # Group by country and sum total sales again for the filtered dataset
    # country_sales = filtered_df.groupby('Country')['CustomerID'].unique().reset_index()
    # country_sales['iso_alpha'] = country_sales['Country'].apply(get_iso_alpha_3)
    country_customers = filtered_df.groupby('Country')['CustomerID'].nunique().reset_index()
    country_customers.rename(columns={'CustomerID': 'Number_of_Customers'}, inplace=True)
    country_customers['iso_alpha'] = country_customers['Country'].apply(get_iso_alpha_3)
    
    
    # Generate a new choropleth figure based on the filtered dataset
    bubble_fig = px.choropleth(country_customers, locations='iso_alpha',
                        color='Number_of_Customers',
                        hover_name='Country', 
                        projection='natural earth',
                        )
    
    bubble_fig.update_layout(
        title={
            'text': 'Customer Segmentation Heatmap',
            'y':0.95,
            'x':0.43,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                #'family': 'Arial, sans-serif',
                'size':24,
                'color': 'black'
            }
        },
        plot_bgcolor='lightblue')  # Changes the plot's background color
        
    
    return bubble_fig
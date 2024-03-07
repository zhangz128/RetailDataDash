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
import pathlib
import pmdarima as pm


PATH = pathlib.Path(__file__).parent.parent.parent
DATA_PATH = PATH.joinpath('data').resolve()
df = pd.read_csv(DATA_PATH.joinpath('raw/online_retail.csv'))
rfm = pd.read_csv(DATA_PATH.joinpath('processed/processed_rfm_model.csv'))

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

monthly_sales = df_ts['Total_Sale'].resample('M').sum()

def get_iso_alpha_3(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except LookupError:
        return None
    
df['iso_alpha'] = df['Country'].apply(get_iso_alpha_3)

def iso_to_country_name(iso_alpha):
    try:
        return pycountry.countries.get(alpha_3=iso_alpha).name
    except:
        return None

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


dash.register_page(__name__, path='/page-1', external_stylesheets=external_stylesheets) # '/' is home page

cluster_mapping = {
    i: cluster for i, cluster in enumerate(
        ['lost customer', 'loyal customer', 'new customer', 'potential loyal customer'])}

country_sales = df.groupby('iso_alpha').agg({'Total_Sale':'sum'}).reset_index()
country_sales['country_name'] = country_sales['iso_alpha'].apply(iso_to_country_name)
country_name_mapping = df[['iso_alpha', 'Country']].drop_duplicates().set_index('iso_alpha')['Country'].to_dict()

# # Create a choropleth map
# global_map_fig = px.choropleth(country_sales,
#                                locations='iso_alpha',
#                                color='Total_Sale',
#                                hover_name='country_name',
#                                projection='natural earth',
#                                title='Map Selector')

# global_map_fig.update_layout(
#     width=800,  # or whatever width suits your layout
#     height=600,  # or whatever height suits your layout
# )

# # Adjust the position of the color bar
# global_map_fig.update_layout(
#     coloraxis_colorbar=dict(
#         x=-0.15,  # Values are between -2 and 3, adjust as needed to move the color bar closer
#         y=0.5,
#         lenmode='fraction',  # Use 'fraction' to scale the color bar size relative to the plot
#         len=0.7,  # Length of the color bar (70% of the plot height in this case)
#     )
# )

layout = html.Div([
    # dcc.Dropdown(
    #     id='country-selector',
    #     options=[{'label': country, 'value': country} for country in df['Country'].unique()],
    #     value=df['Country'].unique()[0]  
    # ),
    # dcc.Graph(id='global-map'),
    # dbc.Row([
    #     dbc.Col([
    #         dcc.Slider(
    #             id='cluster-slider',
    #             min=0,
    #             max=len(cluster_mapping) - 1,  # Since index starts at 0
    #             value=0,  # Default value
    #             marks={i: name for i, name in cluster_mapping.items()},  # Assuming cluster_mapping is a list or similar
    #             step=1  # Force selection of only integer positions
    #         )
    #     ], width=8),
    # ]),
    dbc.Row(
        dbc.Col(
            dcc.Graph(id='global-map', style={'margin-bottom': '0px'}),  # Adjust bottom margin as needed
            width=10
        ),
        justify="center"  # This will center the column for the graph within the row
    ),
    dbc.Row(
        dbc.Col(
            html.Div(
                dcc.Slider(
                    id='cluster-slider',
                    min=0,
                    max=len(cluster_mapping) - 1,  # Since index starts at 0
                    value=0,  # Default value
                    marks={i: name for i, name in cluster_mapping.items()},  # Assuming cluster_mapping is a dict
                    step=1  # Force selection of only integer positions
                ),
                style={'margin-top': '0px', 'margin-bottom': '0px'}  # Adjust top and bottom margin as needed
            ),
            width=8
        ),
        justify="center"  # This will center the slider row
    ),


    dbc.Row([
        dbc.Col([
            dcc.Graph(id='sales_trend_ts')
        ], width=8),
        dbc.Col([
            dcc.Graph(id='cluster_pie')
        ], width=4)
    ])
])

   

@callback(
    [Output('sales_trend_ts', 'figure'),
     Output('cluster_pie', 'figure')],
    [Input('global-map', 'clickData')]
    #[Input('country-selector', 'value')]
)
def update_figures(clickData):
    base_layout = dict(
    paper_bgcolor='rgb(34, 67, 74)',  
    plot_bgcolor='rgb(34, 67, 74)', 
    font=dict(color='white'),  
)

    if clickData is not None:
        country_code = clickData['points'][0]['location']
        selected_country = country_name_mapping.get(country_code, "Unknown")
        filtered_df = df[df['iso_alpha'] == country_code]

        df_ts = filtered_df[['InvoiceDate', 'Total_Sale']]
        df_ts['InvoiceDate'] = pd.to_datetime(df_ts['InvoiceDate'])
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
               marker=dict(color='rgba(248,191,93,0.7)'),             
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
            **base_layout,    
            title={
            'text': f'Sales Trend for {selected_country}',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                #'family': 'Arial, sans-serif',
                'size':24,
                
            }
        },     
        xaxis_title='Month',     
        yaxis_title='Sales',
        )

        cluster_counts = filtered_df['Cluster'].value_counts().reset_index()
        cluster_counts.columns = ['Cluster', 'count']
        custom_colors = ['#dc541b','#2e7d5e','#de9f37','#FFF7C5']
        pie_fig=px.pie(cluster_counts, 
                   values='count', 
                   names='Cluster',
                   color_discrete_sequence=custom_colors                  
                   )
        pie_fig.update_layout(
            **base_layout,
            margin=dict(l=0, r=0, t=20, b=20),
            title={
                'text': f'Costumer Segmentation <br> for {selected_country}',
                'y':0.9,
                'x':0.43,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    #'family': 'Arial, sans-serif',
                    'size':20,
                }
            },
    )
    
        return trend_fig, pie_fig
    else:
        # Return default empty figures
        fig_bar = go.Figure()
        fig_bar.update_layout(**base_layout)
    
        fig_pie = go.Figure()
        fig_pie.update_layout(**base_layout)
        return fig_bar, fig_pie
        
    
# def update_sales_trend(selected_country):
#     filtered_df = df[df['Country'] == selected_country]
#     df_ts = filtered_df[['InvoiceDate', 'Total_Sale']]
#     df_ts.set_index('InvoiceDate', inplace=True)
#     day_sales = df_ts['Total_Sale'].resample('D').sum()
#     day_diff_sales = day_sales.diff().dropna()

#     model = SARIMAX(day_diff_sales, order=(0,0,2), seasonal_order=(1,0,2,7)) 
#     model_fit = model.fit(disp=False)  
#     forecast = model_fit.forecast(steps=82)
#     forecast_df = pd.DataFrame(forecast)
#     forecast_df.rename(columns={'predicted_mean': 'Total_Sale'}, inplace=True)
#     df_ts = df_ts.combine_first(forecast_df)

#     monthly_sales = df_ts['Total_Sale'].resample('ME').sum() 
#     trend_fig = make_subplots(specs=[[{"secondary_y": False}]]) 
#     trend_fig.add_trace(          
#         go.Bar(x=monthly_sales.index[:-3],             
#                y=monthly_sales[:-3],
#                marker=dict(color='rgba(27, 171, 210, 0.7)'),             
#                name='Monthly Sales'),          
#                secondary_y=False,      
#                ) 
#     trend_fig.add_trace(          
#         go.Bar(                  
#             x=monthly_sales.index[-3:],                   
#             y=monthly_sales[-3:],                 
#             marker=dict(color='rgba(255, 0, 0, 0.5)'),
#             name='Prediction'     
#             )) 
#     trend_fig.add_trace(          
#         go.Scatter(x=monthly_sales.index, y=monthly_sales, line=dict(color='rgba(0,143,140,1)')),          
#         secondary_y=False,           
#         ) 
    
#     trend_fig.update_layout(    
#         title={
#             'text': f'Sales Trend for {selected_country}',
#             'y':0.9,
#             'x':0.5,
#             'xanchor': 'center',
#             'yanchor': 'top',
#             'font': {
#                 #'family': 'Arial, sans-serif',
#                 'size':24,
#                 'color': 'black'
#             }
#         },     
#         xaxis_title='Month',     
#         yaxis_title='Sales',
#         paper_bgcolor='rgba(255,255,255,1)',
#         plot_bgcolor='rgba(237,249,253,1)',
#         )
    
#     cluster_counts = filtered_df['Cluster'].value_counts().reset_index()
#     cluster_counts.columns = ['Cluster', 'count']
#     custom_colors = ['#AAE5F4','#4991BA','#FFC357','#FFF7C5']
#     pie_fig=px.pie(cluster_counts, 
#                    values='count', 
#                    names='Cluster',
#                    color_discrete_sequence=custom_colors                  
#                    )
    
#     pie_fig.update_layout(
#         title={
#             'text': f'Cluster Segmentation <br> for {selected_country}',
#             'y':0.9,
#             'x':0.43,
#             'xanchor': 'center',
#             'yanchor': 'top',
#             'font': {
#                 #'family': 'Arial, sans-serif',
#                 'size':20,
#                 'color': 'black'
#             }
#         }
#     )
#     return [trend_fig, pie_fig]

@callback(
    Output('global-map', 'figure'),
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
    
    global_map_fig = px.choropleth(country_customers,
                                   locations='iso_alpha',
                                   color='Number_of_Customers',
                                   hover_name='Country',  # Make sure this is a column in country_sales
                                   projection='natural earth',
                                   )
    global_map_fig.update_geos(
    lataxis_showgrid=False, lonaxis_showgrid=False,
    lataxis_range=[-90, 90],  # These are example ranges, adjust as necessary
    lonaxis_range=[-180, 180],  # These are example ranges, adjust as necessary
)
    # Update the layout of the figure to adjust map size and color bar position
    global_map_fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
        projection_scale=1,  # This controls the scale of the geo projection
        center=dict(lat=0, lon=0),  # This can shift the center of the map
        fitbounds="locations",
        bgcolor='rgb(34, 67, 74)',
        showland=True, landcolor='#f4ecce', 
        showocean=True, oceancolor='#aac8d2',  
    ),
        #width=1000,  # Adjust width to suit your layout
        #height=600,  # Adjust height to suit your layout
        coloraxis_colorbar=dict(
            x=1.2,  # Adjust as needed to move the color bar closer
            y=0.5,
            lenmode='fraction',  # Use 'fraction' to scale the color bar size relative to the plot
            len=0.7,  # Length of the color bar (70% of the plot height in this case)
        ),
        paper_bgcolor='rgb(34, 67, 74)',
        #plot_bgcolor='rgb(34, 67, 74)',
    )
    
    # # Generate a new choropleth figure based on the filtered dataset
    # bubble_fig = px.choropleth(country_customers, locations='iso_alpha',
    #                     color='Number_of_Customers',
    #                     hover_name='Country', 
    #                     projection='natural earth',
    #                     )
    
    # bubble_fig.update_layout(
    #     title={
    #         'text': 'Customer Segmentation Heatmap',
    #         'y':0.95,
    #         'x':0.43,
    #         'xanchor': 'center',
    #         'yanchor': 'top',
    #         'font': {
    #             #'family': 'Arial, sans-serif',
    #             'size':24,
    #             'color': 'black'
    #         }
    #     },
    #     plot_bgcolor='lightblue')  # Changes the plot's background color
        
    
    return global_map_fig
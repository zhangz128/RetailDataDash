import pandas as pd
import numpy as np
import dash
from dash import Dash, html, dash_table, dcc, callback
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objs as go 
from plotly.subplots import make_subplots
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pycountry
import os

path = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(path + '/../../data/raw/online_retail.csv')
rfm = pd.read_csv(path + '/../../data/processed/processed_rfm_model.csv')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['Total_Sale']=df['Quantity']*df['UnitPrice']
df=df.merge(rfm[['CustomerID', 'Cluster']], on='CustomerID', how='left')
df=df[df['Total_Sale']!=0]
df=df[df['Total_Sale']>=0]

df['Year'] = df['InvoiceDate'].dt.year
years = df['Year'].unique()
years.sort()


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

cluster_mapping = {0: 'total customer', 1: 'lost customer', 2: 'loyal customer', 
                   3: 'new customer', 4: 'potential loyal customer'}
    #{i: cluster for i, cluster in enumerate(
    #    ['lost customer', 'loyal customer', 'new customer', 'potential loyal customer'])}

country_sales = df.groupby('iso_alpha').agg({'Total_Sale':'sum'}).reset_index()
country_sales['country_name'] = country_sales['iso_alpha'].apply(iso_to_country_name)
country_name_mapping = df[['iso_alpha', 'Country']].drop_duplicates().set_index('iso_alpha')['Country'].to_dict()


layout = html.Div([
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
                    max=len(cluster_mapping) -1 ,  # Since index starts at 0
                    value=0,  # Default value
                    marks={i: name for i, name in cluster_mapping.items()},
                    # Assuming cluster_mapping is a dict
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
        monthly_sales = df_ts['Total_Sale'].resample('M').sum()

        trend_fig = go.Figure()
        trend_fig.add_trace(
            go.Bar(x=monthly_sales.index, 
                   y=monthly_sales.values, 
                   marker=dict(color='rgba(248,191,93,0.7)'), 
                   name='Monthly Sales',
                   hovertemplate='%{y}<extra></extra>'))
        trend_fig.add_trace(
            go.Scatter(x=monthly_sales.index, 
                       y=monthly_sales.values, 
                       mode='lines+markers',
                       marker=dict(color='rgba(0,143,140,1)'),
                       name='Sales Trend',
                       hovertemplate='%{y}<extra></extra>'))
        trend_fig.update_layout(
            **base_layout,    
            title={
                'text': f'Sales Trend for {selected_country}',
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    'size':24,
                }
            },     
            xaxis_title='Month',     
            yaxis_title='Sales',
        )
        cluster_counts = filtered_df.groupby('Cluster')['CustomerID'].nunique().reset_index()
        cluster_counts.columns = ['Cluster', 'count']
        custom_colors = ['#dc541b','#2e7d5e','#de9f37','#FFF7C5']
        pie_fig=px.pie(cluster_counts, 
                values='count', 
                names='Cluster',
                color_discrete_sequence=custom_colors                  
                )
        pie_fig.update_traces(domain=dict(x=[0.1, 0.9], y=[0.2, 0.8]))
        pie_fig.update_layout(
            **base_layout,
            margin=dict(l=0, r=0, t=20, b=20),
            title={
                'text': f'Customer Segmentation <br> for {selected_country}',
                'y':0.93,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    #'family': 'Arial, sans-serif',
                    'size':20,
                }
            },
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=0,
                xanchor='center',
                x=0.5,
                font=dict(size=10)
            )
        )
    
        return trend_fig, pie_fig
    else:
        df_ts = df[['InvoiceDate', 'Total_Sale']]
        df_ts['InvoiceDate'] = pd.to_datetime(df_ts['InvoiceDate'])
        df_ts.set_index('InvoiceDate', inplace=True)
        monthly_sales = df_ts['Total_Sale'].resample('M').sum()
        trend_fig = go.Figure()
        trend_fig.add_trace(
            go.Bar(x=monthly_sales.index, 
                   y=monthly_sales.values, 
                   marker=dict(color='rgba(248,191,93,0.7)'), 
                   name='Monthly Sales',
                   hovertemplate='%{y}<extra></extra>'))
        trend_fig.add_trace(
            go.Scatter(x=monthly_sales.index, 
                       y=monthly_sales.values, 
                       mode='lines+markers',
                       marker=dict(color='rgba(0,143,140,1)'),
                       name='Sales Trend',
                       hovertemplate='%{y}<extra></extra>'))
        trend_fig.update_layout(
            **base_layout,    
            title={
                'text': 'Sales Trend in Total',
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    'size':24,
                }
            },
            xaxis_title='Month',     
            yaxis_title='Sales',
        )
        
        cluster_counts = df.groupby('Cluster')['CustomerID'].nunique().reset_index()
        cluster_counts.columns = ['Cluster', 'count']
        custom_colors = ['#dc541b','#2e7d5e','#de9f37','#FFF7C5']
        pie_fig=px.pie(cluster_counts, 
                values='count', 
                names='Cluster',
                color_discrete_sequence=custom_colors                  
                )
        pie_fig.update_traces(domain=dict(x=[0.1, 0.9], y=[0.2, 0.8]))
        pie_fig.update_layout(
            **base_layout,
            margin=dict(l=0, r=0, t=20, b=20),
            title={
                'text': f'Customer Segmentation <br> in Total',
                'y':0.93,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    #'family': 'Arial, sans-serif',
                    'size':20,
                }
            },
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=0,
                xanchor='center',
                x=0.5,
                font=dict(size=10)
            )
        )

        return trend_fig, pie_fig
        

@callback(
    Output('global-map', 'figure'),
    [Input('cluster-slider', 'value')]
)
def update_map(selected_segment):
    if selected_segment == 0:
        filtered_df = df.copy()
    else:
        cluster_name = cluster_mapping[selected_segment]
        filtered_df = df[df['Cluster'] == cluster_name]  # Example filter, adjust to your dataframe
    
    # Group by country and sum total sales again for the filtered dataset
    country_sales = filtered_df.groupby('Country')['Total_Sale'].sum().reset_index()
    country_sales['iso_alpha'] = country_sales['Country'].apply(get_iso_alpha_3)
    # country_customers = filtered_df.groupby('Country')['CustomerID'].nunique().reset_index()
    # country_customers.rename(columns={'CustomerID': 'Number_of_Customers'}, inplace=True)
    # country_customers['iso_alpha'] = country_customers['Country'].apply(get_iso_alpha_3)
    min_value = country_sales['Total_Sale'].min()
    max_value = country_sales['Total_Sale'].max()
    tick_values = np.linspace(min_value, max_value, num=50)

    global_map_fig = px.choropleth(country_sales,
                                   locations='iso_alpha',
                                   color='Total_Sale',
                                   hover_name='Country', 
                                   projection='natural earth',
                                   range_color=[0, 500000]
                                   )
    global_map_fig.update_geos(
    lataxis_showgrid=False, lonaxis_showgrid=False,
    lataxis_range=[-90, 90],  
    lonaxis_range=[-180, 180],  
)
    # Update the layout of the figure to adjust map size and color bar position
    global_map_fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
        projection_scale=1,  # This controls the scale of the geo projection
        center=dict(lat=54, lon=15),  # This can shift the center of the map
        fitbounds="locations",
        bgcolor='rgb(34, 67, 74)',
        showland=True, landcolor='#f4ecce', 
        showocean=True, oceancolor='#aac8d2',  
    ),
        #width=1000,  # Adjust width 
        #height=600,  # Adjust height 
        coloraxis_colorbar=dict(
            x=1.0,  # Adjust as needed to move the color bar closer
            y=0.5,
            lenmode='fraction',  # Use 'fraction' to scale the color bar size relative to the plot
            len=0.7,  # Length of the color bar (70% of the plot height in this case)
            title='Sales', 
            ticks='outside', 
            tickvals=tick_values,
            ticktext=[f"{val:,.0f}" for val in tick_values],
            tickfont=dict(size=12, color='white',)
        ),
        paper_bgcolor='rgb(34, 67, 74)',
        #plot_bgcolor='rgb(34, 67, 74)',
    )
    
    return global_map_fig
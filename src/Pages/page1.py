import pandas as pd
import dash
from dash import Dash, html, dash_table, dcc, callback
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import os

SOLAR = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/solar/bootstrap.min.css"
path = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(path + '/../../data/raw/online_retail.csv')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

rfm = pd.read_csv(path + '/../../data/processed/processed_rfm_model.csv')
cluster_counts = rfm['Cluster'].value_counts()

loyal_count = cluster_counts.get('loyal customer', 0)
potential_count = cluster_counts.get('potential loyal customer', 0)
lost_count = cluster_counts.get('lost customer', 0)
new_count = cluster_counts.get('new customer', 0)


card_loyal = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Loyal Costumers", className="card-title text-primary"),
            html.H1(loyal_count, style={'color': '#ffc64b'}),
        ], className="border-start border-info border-5",
    ),
    className="text-center"
)


card_potential = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Potential Loyal", className="card-title text-primary"),
            html.H1(potential_count, style={'color': '#ffc64b'}),
        ], className="border-start border-info border-5"
    ),
    className="text-center",
)


card_new = dbc.Card(
    dbc.CardBody(
        [
            html.H4("New Costumers", className="card-title text-primary"),
            html.H1(new_count, style={'color': '#ffc64b'}),
        ], className="border-start border-info border-5"
    ),
    className="text-center",
)

card_loss = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Loss Costumers", className="card-title text-primary"),
            html.H1(lost_count, style={'color': '#ffc64b'}),
        ], className="border-start border-info border-5"
    ),
    className="text-center",
)

dash.register_page(__name__, path='/', name='Home') # '/' is home page

layout = html.Div(
    [
        html.Div([
            html.Label('Select Date Range:', style={'fontSize': '25px', 'marginRight': '10px'}),
            dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=df['InvoiceDate'].min(),
                max_date_allowed=df['InvoiceDate'].max(),
                start_date=df['InvoiceDate'].min(),
                end_date=df['InvoiceDate'].max(),
                display_format='YYYY-MM-DD',
                start_date_placeholder_text='Start Period',
                end_date_placeholder_text='End Period',
            )],
            style={'marginBottom': '30px'}  
        ),

        dbc.Row(
            [dbc.Col(card_loyal, width=3), dbc.Col(card_potential, width=3),
             dbc.Col(card_new, width=3), dbc.Col(card_loss, width=3)],
        ),

        html.Br(),

        dbc.Row(
    [
        dbc.Col(
            html.Div(
                dcc.Graph(id='top_product'),
                className="bg-dark text-white"
            ), width=6
        ),

        dbc.Col(
            html.Div(
                dcc.Graph(id='top_region'),
                className="bg-dark text-white"
            ), width=6
        )
    ]
)
    ]
)

@callback(
    [Output('top_product', 'figure'),
     Output('top_region', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_figures(start_date, end_date):
    # Filter the dataframe based on the selected date range
    filtered_df = df[(df['InvoiceDate'] >= start_date) & (df['InvoiceDate'] <= end_date)]
    
    # Calculate top products
    top_products = filtered_df.groupby('Description')['Quantity'].sum().reset_index().nlargest(10, 'Quantity')
    fig_top_product = px.bar(top_products, x='Quantity', y='Description', orientation='h', title='Top 10 Products')

    # Calculate top countries
    top_countries = filtered_df.groupby('Country')['Quantity'].sum().reset_index().nlargest(10, 'Quantity')
    fig_top_region = px.bar(top_countries, x='Quantity', y='Country', orientation='h', title='Top 10 Regions')

    # Update layout for both figures
    for fig in [fig_top_product, fig_top_region]:
        for trace in fig.data:
            trace.marker.color = 'rgba(248,191,93,0.7)' 

        fig.update_layout(
            yaxis={'categoryorder':'total ascending', 'showgrid': False}, 
            #xaxis={'showgrid': False},
            yaxis_title="",
            title_font={'size': 24, 'color': '#f8bf5d', 'family': "Arial, sans-serif"},
            paper_bgcolor='rgb(34, 67, 74)',  # Bootstrap's `.bg-dark` color
            plot_bgcolor='rgb(34, 67, 74)',
            font=dict(color='white'),
            #paper_bgcolor='rgba(255,255,255,1)',  # Set the background around the plot to white
            #plot_bgcolor='rgba(237,249,253,1)',
            title_x=0.5
        )

    return fig_top_product, fig_top_region


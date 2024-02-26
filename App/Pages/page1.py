import pandas as pd
import dash
from dash import Dash, html, dash_table, dcc, callback
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc



df = pd.read_csv('online_retail.csv')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

rfm = pd.read_csv('processed_rfm_model.csv')
cluster_counts = rfm['Cluster'].value_counts()

loyal_count = cluster_counts.get('loyal customer', 0)
potential_count = cluster_counts.get('potential loyal customer', 0)
lost_count = cluster_counts.get('lost customer', 0)
new_count = cluster_counts.get('new customer', 0)

# top_products = df.groupby('Description')['Quantity'].sum().reset_index().nlargest(10, 'Quantity')

# top_countries = df.groupby('Country')['Quantity'].sum().reset_index().nlargest(10, 'Quantity')

# # Sort the DataFrame
# top_countries_sorted = top_countries.sort_values('Quantity', ascending=False)
# top_products_sorted = top_products.sort_values('Quantity', ascending=False)


# #fig_pricing = px.scatter(df, x='UnitPrice', y='Quantity', title='Pricing Elasticity')
# fig_top_product = px.bar(top_products_sorted, x='Quantity', y='Description', orientation='h', title='Top Product')
# fig_top_region = px.bar(top_countries_sorted, x='Quantity', y='Country', orientation='h', title='Top Region')

# fig_top_region.update_layout(
#     title={
#         'text': 'Top 10 Regions',
#         'y':0.9,
#         'x':0.5,
#         'xanchor': 'center',
#         'yanchor': 'top',
#         'font': {'size': 24, 'color': 'black', 'family': "Arial, sans-serif"}  
#     },
#     yaxis={'categoryorder':'total ascending'}, yaxis_title=""
# )

# fig_top_product.update_layout(
#     title={
#         'text': 'Top 10 Products',
#         'y':0.9,
#         'x':0.5,
#         'xanchor': 'center',
#         'yanchor': 'top',
#         'font': {'size': 24, 'color': 'black', 'family': "Arial, sans-serif"}  
#     },
#     yaxis={'categoryorder':'total ascending'}, yaxis_title=""
# )

# fig_pricing.update_layout(
#     title={
#         'text': 'Price Elasticity',
#         'y':0.9,
#         'x':0.5,
#         'xanchor': 'center',
#         'yanchor': 'top',
#         'font': {'size': 24, 'color': 'black', 'family': "Arial, sans-serif"}  
#     },
#     yaxis={'categoryorder':'total ascending'}
# )

# CONTENT_STYLE = {
#     "margin-left": "18rem",
#     "margin-right": "2rem",
#     "padding": "2rem 1rem",
# }

# content = html.Div(id="page-content", children=[
#     html.H1(children='ONLINE RETAIL SALES DATA', style={'textAlign': 'center',
#                                                          'color': 'white', 
#                                                          'background-color':'skyblue'}),
    
#     html.Div([
#         html.Div([
#             dcc.Graph(figure=fig_pricing, style={'height': '400px'}),
#         ], className='col-md-6', style={'padding': '10px'}),
#         html.Div([
#             dcc.Graph(figure=fig_top_product, style={'height': '500px'}),
#             dcc.Graph(figure=fig_top_region, style={'height': '500px'}),
#         ], className='col-md-6', style={'padding': '10px'}),
#     ], className='row', style={'marginTop': '20px'})
# ], style=CONTENT_STYLE)

card_loyal = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Loyal Costumers"),
            html.H1(loyal_count),
        ], className="border-start border-info border-5"
    ),
    className="text-center"
)


card_potential = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Potential Loyal"),
            html.H1(potential_count),
        ], className="border-start border-info border-5"
    ),
    className="text-center",
)


card_new = dbc.Card(
    dbc.CardBody(
        [
            html.H4("New Costumers"),
            html.H1(new_count),
        ], className="border-start border-info border-5"
    ),
    className="text-center",
)

card_loss = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Loss Costumers"),
            html.H1(lost_count),
        ], className="border-start border-info border-5"
    ),
    className="text-center",
)

dash.register_page(__name__, path='/', name='Home') # '/' is home page

layout = html.Div(
    [
    	dbc.Row(
            [dbc.Col(card_loyal, width=3), dbc.Col(card_potential, width=3),
             dbc.Col(card_new, width=3), dbc.Col(card_loss, width=3)],
        ),

        html.Br(),
        
        dcc.DatePickerRange(
        id='date-picker-range',
        min_date_allowed=df['InvoiceDate'].min(),
        max_date_allowed=df['InvoiceDate'].max(),
        start_date=df['InvoiceDate'].min(),
        end_date=df['InvoiceDate'].max(),
        display_format='YYYY-MM-DD',
        start_date_placeholder_text='Start Period',
        end_date_placeholder_text='End Period',
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

        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id='top_product')
                    ], width=6
                ),

                dbc.Col(
                    [
                        dcc.Graph(id='top_region')
                    ], width=6
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
            trace.marker.color = 'rgba(27, 171, 210, 0.7)'

        fig.update_layout(
            yaxis={'categoryorder':'total ascending', 'showgrid': False}, 
            #xaxis={'showgrid': False},
            yaxis_title="",
            title_font={'size': 24, 'color': 'black', 'family': "Arial, sans-serif"},
            paper_bgcolor='rgba(255,255,255,1)',  # Set the background around the plot to white
            plot_bgcolor='rgba(237,249,253,1)',
            title_x=0.5
        )

    return fig_top_product, fig_top_region

# @callback(Output("page-content", "children"), [Input("url", "pathname")])
# def render_page_content(pathname):
#     if pathname == "/":
#         return html.P(content)
#     elif pathname == "/page-1":
#         return html.P("This is the content of page 1. Yay!")
#     elif pathname == "/page-2":
#         return html.P("Oh cool, this is page 2!")
#     # If the user tries to reach a different page, return a 404 message
#     return html.Div(
#         [
#             html.H1("404: Not found", className="text-danger"),
#             html.Hr(),
#             html.P(f"The pathname {pathname} was not recognised..."),
#         ],
#         className="p-3 bg-light rounded-3",
#     )
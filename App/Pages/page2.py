import pandas as pd
import dash
from dash import Dash, html, dash_table, dcc, callback
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

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

        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id='fig_trend')
                    ], width=12
                ),

                # dbc.Col(
                #     [
                #         dcc.Graph(id='top_region')
                #     ], width=6
                # )
            ]
        )
    ]
)

@callback(
    [Output('fig_trend', 'figure')],
    [Input('country-selector', 'value')]
)
def update_sales_trend(selected_country):
    filtered_df = df[df['Country'] == selected_country]
    monthly_revenue = filtered_df.resample('ME', on='InvoiceDate')['Total_Sale'].sum().reset_index()

    fig_trend = px.line(monthly_revenue, x='InvoiceDate', y='Total_Sale', markers=True, line_shape='linear', title=f'Monthly Revenue Trend for {selected_country}')

    fig_trend.update_layout(
        xaxis_title='Month',
        yaxis_title='Total Revenue',
        xaxis=dict(tickangle=-45, title_font=dict(size=14), tickfont=dict(size=12)),
        yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12))
    )
    
    return [fig_trend]
import pandas as pd
import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import altair as alt



sidebar = dbc.Nav(
        
        [
            dbc.NavLink("Overview", href="/", active="exact"),
            dbc.NavLink("Region Information", href="/page-1", active="exact"),
            dbc.NavLink("Other", href="/page-2", active="exact"),
        ],
        vertical=True,
        pills=True,
        className="bg-light"
)



app1 = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SPACELAB])

app1.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.Div('ONLINE RETAIL SALES DATA', style={'textAlign': 'center', 'fontSize':50, 
                                                         'color': 'white', 
                                                         'background-color':'skyblue'}))
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            sidebar
        ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),

        dbc.Col([
            dash.page_container
        ], xs=8, sm=8, md=10, lg=10, xl=10, xxl=10)])
    ], 
fluid=True)


if __name__ == '__main__':
    app1.run_server(debug=True, port=8051)




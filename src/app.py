import pandas as pd
import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import altair as alt

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f0f0f0",
}

CONTENT_STYLE = {
    "margin-left": "0rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

HEADER_STYLE = {
    "padding": "20px",
    "fontSize": "60px",
    "textAlign": "center",
    "background": "#F0F0F0",
    "color": "#125B77",
}

header = html.Div("ONLINE RETAIL SALES DATA", style=HEADER_STYLE)

sidebar = dbc.Nav(
        
        [ 
            html.H4("Sales Analysis"),
            html.Hr(),
            html.P("Analytic Graph Providing a Deeper Understanding on Sales in Global"),
            #html.Hr(),
            dbc.NavLink("Overview", href="/", active="exact"),
            dbc.NavLink("Region Information", href="/page-1", active="exact"),
            #dbc.NavLink("Other", href="/page-2", active="exact"),
        ],
        vertical=True,
        pills=True,
        style=SIDEBAR_STYLE,
)



app = dash.Dash(__name__, use_pages=True, pages_folder="Pages", external_stylesheets=[dbc.themes.SPACELAB])
server = app.server


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            sidebar
        ], #xs=4, sm=4, md=2, lg=2, xl=2, xxl=2
        ),

        dbc.Col([
            dbc.Row([header]),
            #dash.page_container
            dbc.Row([html.Div(dash.page_container, style=CONTENT_STYLE)])
        ], xs=8, sm=8, md=10, lg=10, xl=10, xxl=10)])
    ], 
fluid=True)

if __name__ == '__main__':
    app.run_server(debug=False)




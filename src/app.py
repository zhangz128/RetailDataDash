import pandas as pd
import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import altair as alt

SOLAR = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/solar/bootstrap.min.css"


# SIDEBAR_STYLE = {
#     "position": "fixed",
#     #"top": "75px",
#     "top": 0,
#     "left": 0,
#     "bottom": 0,
#     "width": "16rem",
#     "padding": "2rem 1rem",
#     "background-color": "#D9E8E9",
#     "overflow-y": "auto",
# }

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#011a21",
}

# CONTENT_STYLE = {
#     "margin-left": "0rem",
#     "margin-right": "2rem",
#     "padding": "2rem 1rem",
# }

HEADER_STYLE = {
    "padding": "20px",
    "fontSize": "60px",
    "textAlign": "center",
    #"background": "#F0F0F0",
    #"color": "#125B77",
}

header = html.Div("ONLINE RETAIL SALES DATA", style=HEADER_STYLE)


sidebar = dbc.Nav(
        
        [ 
            html.H3("Sales Analysis", className="text-secondary"),
            html.Hr(),
            html.P("Analytic Graph Providing a Deeper Understanding on Sales in Global"),
            #html.Hr(),
            dbc.NavLink("Overview", href="/", active="exact"),
            dbc.NavLink("Region Information", href="/page-1", active="exact"),
            #dbc.NavLink("Other", href="/page-2", active="exact"),
        ],
        vertical=True,
        pills=True,
        #className="bg-light",
        style=SIDEBAR_STYLE,
)



app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SPACELAB, SOLAR])

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    sidebar,
                    xs=4, sm=4, md=2, lg=2, xl=2, xxl=2  # Adjust sizes for smaller screens
                ),
                dbc.Col(
                    [
                        dbc.Row(header),  # Header row
                        dbc.Row(html.Div(dash.page_container))  # Page container row
                    ],
                    xs=8, sm=8, md=10, lg=10, xl=10, xxl=10,  # Adjust sizes for content on different screens
                    style={'marginLeft': '16rem'}  # Add marginLeft to account for the sidebar
                )
            ],
            className="g-0",  # This is how you could normally remove gutters in Bootstrap 5, but it seems not to be supported in your version of dbc
        )
    ],
    fluid=True
)


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)




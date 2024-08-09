import dash_bootstrap_components as dbc
from dash import html, dcc

DEVELOPER_EMAIL = "gwhite@fgcz.ethz.ch"

myra_sidebar = [
    dbc.Card(
        id="first-card",
        children=[
            dcc.Dropdown(
                id="dropdown-select-file-type",
                options=[
                    {
                        "label": "Normalization",
                        "value": "norm"
                    },
                    {
                        "label": "Input Normalization",
                        "value": "inorm",
                    },
                    {
                        "label": "Pool",
                        "value": "pool",
                    },
                    {
                        "label": "Repool",
                        "value": "repool",
                    },
                ],
                clearable=False,
                searchable=False,
                value="norm"
            ),
            html.P(),
            dcc.Input(
                id="pool_vol",
                placeholder="desired pooling volume"
            ),
            html.P(),
            # html.Button('Load / Reload', id='load-val-2', n_clicks=0, style={'color':'white'}),
            html.Button('Load / Reload', id='load-val-2', n_clicks=0),
            html.P(),
            dcc.Download(id='download')
        ],
    ),
    dcc.Loading(
        dbc.Card(
            id="mal-card",
            children=[
                
            ]
        ),
    )
]

default_sidebar = [
    html.P(id="sidebar_text", children="Select a Value"),
    dcc.Slider(0, 20, 5, value=10, id='example-slider'),
    html.Br(),
    dcc.Dropdown(['Genomics', 'Proteomics', 'Metabolomics'], 'Genomics', id='example-dropdown'),
    html.Br(),
    dbc.Input(value='Enter Some Text', id='example-input'),
    html.Br(),
    dbc.Button('Submit', id='example-button'),
]

no_auth = [
    html.P("You are not currently logged into an active session. Please log into bfabric to continue:"),
    html.A('Login to Bfabric', href='https://fgcz-bfabric.uzh.ch/bfabric/')
]

expired = [
    html.P("Your session has expired. Please log into bfabric to continue:"),
    html.A('Login to Bfabric', href='https://fgcz-bfabric.uzh.ch/bfabric/')
]

no_entity = [
    html.P("There was an error fetching the data for your entity. Please try accessing the applicaiton again from bfabric:"),
    html.A('Login to Bfabric', href='https://fgcz-bfabric.uzh.ch/bfabric/')
]

dev = [html.P("This page is under development. Please check back later."),html.Br(),html.A("email the developer for more details",href="mailto:"+DEVELOPER_EMAIL)]

auth = [
    html.Div(
        id="graph_header-2",
        children=[

        ]
    ),
    dcc.Loading(
        children = [
            dcc.Store(id='input_df'),
            # dcc.Store(id='edited'),
            # dcc.Store(id='order-number')
        ],
        type="circle"
    ),
    html.Div(
        id="div-graphs-myra",
        children=[
            dcc.Graph(
                id="OUT",
                figure=dict(
                    layout=dict(
                        # plot_bgcolor="#282b38", paper_bgcolor="#282b38"
                    )
                ),
            ),
        ]
    )
]
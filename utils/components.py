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
            dbc.Button('Load / Reload', id='load-val-2', n_clicks=0, color="primary"),
            html.P(),
            dbc.Button('Submit iSeq Selections', disabled=True, id='submit_iseq', n_clicks=0, color="primary", style={"margin-top":"10px", "height":"40px"}),
            html.P(),
            dcc.Download(id='download')
        ],
        style={"padding":"2px", "border":"0px solid #d4d7d9"}
    ),
    dcc.Loading(
        dbc.Card(
            id="mal-card",
            children=[],
            style={"padding":"2px", "border":"0px solid #d4d7d9"}
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
        children=[]
    ),
    dcc.Loading(
        children = [
            dcc.Store(id='input_df'),
            # dcc.Store(id='edited'),
            # dcc.Store(id='order-number')
        ],
        type="circle"
    ),
    dcc.Loading(
        html.Div(
            id="div-graphs-myra",
            children=[
                # dcc.Graph(
                #     id="OUT",
                #     figure=dict(
                #         layout=dict(
                #             # plot_bgcolor="#282b38", paper_bgcolor="#282b38"
                #         )
                #     ),
                # ),
            ],
            style={"padding-right":"40px", "max-width":"60vw"}
        )
    ),
]

main_tab = dbc.Row(
    id="page-content-main",
    children=[
        dbc.Col(
            html.Div(
                id="sidebar",
                children=myra_sidebar,
                style={"border-right": "2px solid #d4d7d9", "height": "100%", "padding": "20px", "font-size": "20px"}
            ),
            width=3,
        ),
        dbc.Col(
            html.Div(
                id="page-content",
                children=no_auth + [html.Div(id="auth-div")],style={"margin-top":"2vh", "margin-left":"2vw", "font-size":"14px", "max-height":"70vh", "height":"70vh", "overflow-y":"scroll"},
            ),
            width=9,
        ),
    ],
    style={"margin-top": "0px", "min-height": "40vh", "max-height":"70vh", "overflow-y":"scroll"}
),

empty_sidebar = []


report_bug_tab = dbc.Row(
    id="page-content-bug-report",
    children=[
        dbc.Col(
            html.Div(
                id="sidebar_bug_report",
                children=empty_sidebar,
                style={"border-right": "2px solid #d4d7d9", "height": "100%", "padding": "20px", "font-size": "20px"}
            ),
            width=3,
        ),
        dbc.Col(
            html.Div(
                id="page-content-bug-report-children",
                children=[
                    html.H2("Report a Bug"),
                    html.P([
                        "Please use the form below to report a bug in the Draugr UI. If you have any questions, please email the developer at ",
                        html.A(" griffin@gwcustom.com", href="mailto:griffin@gwcustom.com"),
                    ]),
                    html.Br(),
                    html.H4("Session Details: "),
                    html.Br(),
                    html.P(id="session-details", children="No Active Session"),
                    html.Br(),
                    html.H4("Bug Description"),
                    dbc.Textarea(id="bug-description", placeholder="Please describe the bug you encountered here.", style={"width": "100%"}),
                    html.Br(),
                    dbc.Button("Submit Bug Report", id="submit-bug-report", n_clicks=0, style={"margin-bottom": "60px"}),
                    html.Br(),
                ],
                style={"margin-top":"2vh", "margin-left":"2vw", "font-size":"20px", "padding-right":"40px"},
            ),
            width=9,
        ),
    ],
    style={"margin-top": "0px", "min-height": "40vh"}
)


docs = dbc.Row(
        id="page-content-docs",
        children=[
            dbc.Col(
                html.Div(
                    id="sidebar_docs",
                    children=empty_sidebar,
                    style={"border-right": "2px solid #d4d7d9", "height": "100%", "padding": "20px", "font-size": "20px"}
                ),
                width=3,
            ),
            dbc.Col(
                [html.Div(
                    id="page-content-docs-children",
                    children=[
                        html.H2("Welcome to The Myra CSV Downloader App"),
                        html.P([
                            "This app serves as a user interface for creating input CSV files for the Myra Robot, using bfabric data."
                        ]),
                        html.Br(),
                        html.H4("Developer Info"),
                        html.P([
                            "This app was written by Griffin White, for the FGCZ. If you wish to report a bug, please use the \"bug reports\" tab. If you wish to contact the developer for other reasons, please use the email:",
                            html.A(" griffin@gwcustom.com", href="mailto:griffin@gwcustom.com"),
                        ]),
                        html.Br(),

                        html.H4("Some Notes on this App\'s Functionality"),
                        html.P([
                            """
                            This app is designed to easily allow users to download Myra CSVs, based on data associated with the respective plate object in Bfabric. """
                        ]),
                        html.Br(),
                        html.H4("CSV Prep Tab"),
                        html.P([
                            "These Docs are still under construction! Please check back later for more information."
                        ]),
                        html.H4("Report a Bug Tab"),
                        html.P([
                            "If you encounter a bug while using this app, please fill out a bug report in the \"Report a Bug\" tab, so that it can be addressed by the developer."
                        ]),
                    ],
                    style={"margin-top":"2vh", "margin-left":"2vw", "padding-right":"40px"},
                ),],
                width=9,
            ),
        ],
    style={"margin-top": "0px", "min-height": "40vh", "height":"70vh", "max-height":"70vh", "overflow-y":"scroll", "padding-right":"40px", "padding-top":"20px"}
)


tabs = dbc.Tabs(
    [
        dbc.Tab(main_tab, label="CSV Prep"),
        dbc.Tab(docs, label="Documentation"),
        dbc.Tab(report_bug_tab, label="Submit Bug Report"),
    ]
)
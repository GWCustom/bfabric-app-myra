from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc
import dash
from dash import dash_table
import json
import os
import bfabric
import pandas as pd
from dash import callback_context as ctx
from utils import auth_utils, components, formatting_functions as fns
from datetime import datetime as dt
from utils.objects import Logger

if os.path.exists("./PARAMS.py"):
    try:
        from PARAMS import PORT, HOST, DEV
    except:
        PORT = 8050
        HOST = 'localhost'
        DEV = True
else:
    PORT = 8050
    HOST = 'localhost'
    DEV = True
    

####### Main components of a Dash App: ########
# 1) app (dash.Dash())
# 2) app.layout (html.Div())
# 3) app.callback()

#################### (1) app ####################
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

#################### (2) app.layout ####################

app.layout = html.Div(
    children=[
        dcc.Location(
            id='url',
            refresh=False
        ),
        dbc.Container(
            children=[    
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            className="banner",
                            children=[
                                html.Div(
                                    children=[
                                        html.P(
                                            'Myra CSV Downloader',
                                            style={'color':'#ffffff','margin-top':'15px','height':'80px','width':'100%',"font-size":"40px","margin-left":"20px"}
                                        )
                                    ],
                                    style={"background-color":"#000000", "border-radius":"10px"}
                                ),
                            ],
                        ),
                    ),
                ),
                dbc.Row(
                    dbc.Col(
                        [
                            html.Div(
                                children=[html.P(id="page-title",children=[str(" ")], style={"font-size":"40px", "margin-left":"20px", "margin-top":"10px"})],
                                style={"margin-top":"0px", "min-height":"80px","height":"6vh","border-bottom":"2px solid #d4d7d9"}
                            ),
                            dbc.Alert(
                                "You're bug report has been submitted. Thanks for helping us improve!",
                                id="alert-fade-3",
                                dismissable=True,
                                is_open=False,
                                color="info",
                                style={"max-width":"50vw", "margin":"10px"}
                            ),
                            dbc.Alert(
                                "Failed to submit bug report! Please email the developers directly at the email below!",
                                id="alert-fade-3-fail", 
                                dismissable=True,
                                is_open=False, 
                                color="danger",
                                style={"max-width":"50vw", "margin":"10px"}
                            ),
                        ]
                    )
                ),
                components.tabs,
            ], style={"width":"100vw"},  
            fluid=True
        ),
        dcc.Store(id='token', storage_type='session'), # Where we store the actual token
        dcc.Store(id='entity', storage_type='session'), # Where we store the entity data retrieved from bfabric
        dcc.Store(id='token_data', storage_type='session'), # Where we store the token auth response
        dcc.Store(id='input_df', storage_type='session'), # Where we store the input dataframe
    ],style={"width":"100vw", "overflow-x":"hidden", "overflow-y":"scroll"}
)

#################### (3) app.callback ####################
@app.callback(
    [
        Output('token', 'data'),
        Output('token_data', 'data'),
        Output('entity', 'data'),
        Output('page-content', 'children'),
        Output('page-title', 'children'),
        Output('session-details', 'children'),
        Output('load-val-2', 'disabled'),
        Output('pool_vol', 'disabled'),
        Output('dropdown-select-file-type', 'disabled')
    ],
    [
        Input('url', 'search'),
    ]
)
def display_page(url_params):
    
    base_title = ""

    if not url_params:
        return None, None, None, components.no_auth, base_title, None, True, True, True
    
    token = "".join(url_params.split('token=')[1:])
    tdata_raw = auth_utils.token_to_data(token)
    
    if tdata_raw:
        if tdata_raw == "EXPIRED":
            return None, None, None, components.expired, base_title, None, True, True, True

        else: 
            tdata = json.loads(tdata_raw)
    else:
        return None, None, None, components.no_auth, base_title, None, True, True, True
    
    if tdata:
        entity_data_json, logger_instance = auth_utils.entity_data(tdata)
        entity_data = json.loads(entity_data_json)
        page_title = f"{tdata['entityClass_data']} - {entity_data['name']} - ID: - {tdata['entity_id_data']}" if tdata else "B-Fabric App Interface"
        session_details = [html.P("No session details available.")]
        if not tdata:
            return token, None, None, components.no_auth, page_title,session_details, True, True, True
        
        elif not entity_data:
            return token, None, None, components.no_entity, page_title,session_details,True, True, True
        
        else:
            if not DEV:
                print(entity_data)
                session_details = [
                    html.P([
                        html.B("Entity Name: "), entity_data['name'],
                        html.Br(),
                        html.B("Entity Class: "), tdata['entityClass_data'],
                        html.Br(),
                        html.B("Environment: "), tdata['environment'],
                        html.Br(),
                        html.B("Entity ID: "), tdata['entity_id_data'],
                        html.Br(),
                        html.B("User Name: "), tdata['user_data'],
                        html.Br(),
                        html.B("Session Expires: "), tdata['token_expires'],
                        html.Br(),
                        html.B("Current Time: "), str(dt.now().strftime("%Y-%m-%d %H:%M:%S"))
                    ])
                ]
                return token, tdata, entity_data, components.auth, page_title,session_details, False, False, False
            else: 
                token_data = json.loads(auth_utils.token_to_data(token))

                if entity_data:
                    return token, tdata, entity_data, components.dev, page_title,session_details, True, True, True
    else: 
        return None, None, None, components.no_auth, base_title,session_details, True, True, True
@app.callback(output=Output("mal-card", "children"),
            state=[State("dropdown-select-file-type", "value"),
                    State("token", "data"),
                    State('token_data', 'data'),
                    State("pool_vol", "value")],
            inputs=[Input("input_df","data")],
            prevent_initial_call=True
            )
def generate_iseq_selectors(data, ftype, token, token_data, pool_vol):

    tdata = json.loads(auth_utils.token_to_data(token))

    if ftype == "repool":
        df = pd.DataFrame(data)
        df = df[df['containerType'] == "order"]
        df['ident'] = [str(i).split("_")[-1] for i in list(df['group'])]
        order_runs = dict()

        wrapper = auth_utils.token_response_to_bfabric(tdata)
        jobId = token_data.get('jobId', None)
        username = token_data.get("user_data", "None")

        L = Logger(jobid=jobId, username=username)

        for order in list(df['ident'].unique()):
            tmp = df[df['ident'] == order]
            runs = []

            try:
                # old api call - ress = wrapper.read("sample", {"tubeid": list(tmp['tubeID']), "includeruns": True, "type": "Library on Run - Illumina"}, max_results=None)

                ress = L.logthis(
                    api_call=wrapper.read,
                    endpoint= "sample",
                    obj={"tubeid": list(tmp['tubeID']), "includeruns": True, "type": "Library on Run - Illumina"},
                    max_results=None,
                    params={"action": ftype, "pooling volume": pool_vol},
                    flush_logs = False
                )

            except Exception as e:
                L.log_operation(
                        "Error",
                        f"Failed to retrieve samples for order {order}. Exception: {e}",
                        params={"action": ftype},
                        flush_logs=False
                )
                ress = []

            if ress:
                for res in ress:
                    # Try to access the 'run' attribute if it exists
                    if 'run' in res:
                        for w in res['run']:
                            try:
                                runs.append(w['id'])
                            except KeyError:
                                L.log_operation(
                                        "Error",
                                        f"Missing 'id' in run data for sample {res.get('id', 'unknown ID')}.",
                                        params={"sample": res},
                                        flush_logs=False
                                )
                                print("Error: Missing '_id' in run data")
                    else:
                        L.log_operation(
                                "Error",
                                f"No 'run' attribute found for sample {res.get('id', 'unknown ID')}.",
                                params={"sample": res},
                                flush_logs=False
                        )
                        print(f"No run attribute found for sample {res.get('id', 'unknown ID')}")
                        
            runs = list(set(runs))
            iseqs = {}

            # Fetch the run data if runs list is populated
            for run in runs:

                #res_run = wrapper.read("run", {"id": str(run)}, max_results=None)

                res_run = L.logthis(
                    api_call=wrapper.read,
                    endpoint= "run",
                    obj={"id": str(run)},
                    max_results=None,
                    params={"action": ftype, "pooling volume": pool_vol},
                    flush_logs = False
                )


                if res_run and "instrument" in res_run[0] and (
                    "iseq" in str(res_run[0]["instrument"]).lower() or str(res_run[0].get("qc", "false")) == "true"
                ):
                    iseqs[str(run)] = res_run[0]["name"]

            if iseqs:
                order_runs[order] = iseqs.copy()

        send = [
            html.Div(
                [   
                    html.P(
                        "Order " + str(order),
                        style={"font-size": "14px", "margin-bottom": "1px"}
                    ),
                    dcc.Dropdown(
                        id="order_" + str(order),
                        options=[{"label": order_runs[order][elt], "value": elt} for elt in order_runs[order]],
                        clearable=False,
                        searchable=False,
                        value="",
                        style={"padding": "2px"}
                    ),
                ],
                style={"margin-bottom": "10px"}
            ) for order in order_runs
        ]
        # send.append(html.Button('Submit iSeq Selections', id='submit_iseq', n_clicks=0))
        L.log_operation(
            "Log",
            "Submit iSeq Selections.",
            params={"action": ftype, "pooling volume": pool_vol, f"Order {order}": iseqs},
            flush_logs=True
        )
        return send
    else:
        # return [html.Button('Submit iSeq Selections', id='submit_iseq', n_clicks=0)]
        return []


@app.callback(
    [
        Output("alert-fade-3", "is_open"),
        Output("alert-fade-3-fail", "is_open")
    ],
    [
        Input("submit-bug-report", "n_clicks")
    ],
    [
        State("token", "data"),
        State("entity", "data"),
        State("bug-description", "value"),
    ],
    prevent_initial_call=True
)
def submit_bug_report(n_clicks, token, entity_data, bug_description):

    if token: 
        token_data = json.loads(auth_utils.token_to_data(token))
    else:
        token_data = ""

    jobId = token_data.get('jobId', None)
    username = token_data.get("user_data", "None")

    L = Logger(jobid=jobId, username=username)

    if n_clicks:
        L.log_operation("bug_report", "Initiating bug report submission process.", params=None, flush_logs=False)
        try:
            sending_result = auth_utils.send_bug_report(
                token_data=token_data,
                entity_data=entity_data,
                description=bug_description
            )
            if sending_result:
                L.log_operation("bug_report", bug_description, params=None, flush_logs=True)
                return True, False
            else:
                L.log_operation("bug_report", "Failed to submit bug report!", params=None, flush_logs=True)
                return False, True
        except:
            L.log_operation("bug_report", "Failed to submit bug report!", params=None, flush_logs=True)
            return False, True

    return False, False


@app.callback(output=[
        Output("input_df", "data"),
        Output("submit_iseq", "disabled"),
    ],
        inputs=[Input("load-val-2", "n_clicks")],
        state=[State("token", "data"),
               State("pool_vol", "value"),
               State("token_data", "data"),
               State("dropdown-select-file-type","value")
    ],
    prevent_initial_call=True
    )

def generate_input_df(start, token, pool_vol, token_data, dropdown):

    tdata = json.loads(auth_utils.token_to_data(token))
    plate = tdata['entity_id_data']

    wrapper = auth_utils.token_response_to_bfabric(tdata)

    df = fns.get_plate_details(plate, pool_vol, wrapper, token_data, dropdown)

    return df.to_dict("records"), False


@app.callback(output=Output("div-graphs-myra", "children"),
              inputs=[Input("input_df","data"),
                      Input('submit_iseq', 'n_clicks')],
              state=[State("dropdown-select-file-type","value"),
                    State("mal-card","children"),
                    State("pool_vol","value"),
                    State("token","data"),
                    State('token_data', 'data')],prevent_initial_call=True)
def generate_table(data, iseq_submit, dropdown, card, pool_vol, token, token_data):

    print("CALLBACK IS RUNNING")

    button_clicked = ctx.triggered_id

    if not data:

        print("NO DATA")
        send = dash_table.DataTable(
                [],
                [],
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(220, 220, 220)',
                    }
                ],
                style_cell={'padding':'10px'},
                style_data={
                    'color': 'black',
                    'backgroundColor': 'white'
                },
                style_header={
                    'backgroundColor': 'rgb(210, 210, 210)',
                    'color': 'black',
                    'fontWeight': 'bold'
                }
            )
        return send

    data = pd.DataFrame(data)
    print(data)

    if dropdown == "norm":
        data = data[data['libraryPassed']=="true"]
        df = fns.Normalize(data)
    elif dropdown == "inorm":
        df = fns.iNormalize(data)
    elif dropdown == "pool":
        data = data[data['libraryPassed']=="true"]
        df = fns.Pool(data)
    elif dropdown == "repool":

        orderRun = dict()
        for child in card:

            if True:
                elt = child['props']['children'][1]
                print(elt)
                print(elt['props']['id'])
                orderRun[elt['props']['id'].split("_")[-1]] = elt['props']['value']
            # except:
            else:
                pass
        if orderRun == dict():
            return

        wrapper = auth_utils.token_response_to_bfabric(json.loads(auth_utils.token_to_data(token)))
        df = fns.RePool(data,orderRun,pool_vol,wrapper, token_data, dropdown)

    send = dash_table.DataTable(
                df.to_dict("records"),
                [{"name": i, "id": i} for i in df.columns],
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(220, 220, 220)',
                    }
                ],
                style_cell={'padding':'10px'},
                style_data={
                    'color': 'black',
                    'backgroundColor': 'white'
                },
                style_header={
                    'backgroundColor': 'rgb(210, 210, 210)',
                    'color': 'black',
                    'fontWeight': 'bold'
                },
                export_format='csv',
                export_headers='display',
                merge_duplicate_headers=True
            )
    return send

if __name__ == '__main__':
    app.run_server(debug=False, port=PORT, host=HOST)

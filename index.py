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
                                children=[html.P(id="page-title",children=[str("Myra CSV Downloader")], style={"font-size":"40px", "margin-left":"20px", "margin-top":"10px"})],
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
        Output('dropdown-select-file-type', 'disabled'),
    ],
    [
        Input('url', 'search'),
    ]
)
def display_page(url_params):
    
    base_title = "Myra CSV Downloader"

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
        entity_data = json.loads(auth_utils.entity_data(tdata))
        page_title = f"{base_title} - {tdata['entityClass_data']} - {tdata['entity_id_data']} ({tdata['environment']} System)" if tdata else "Bfabric App Interface"
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
                     State("token", "data")],
              inputs=[Input("input_df","data")])
def generate_iseq_selectors(data, ftype, token):

    tdata = json.loads(auth_utils.token_to_data(token))

    if ftype == "repool":
        df = pd.DataFrame(data)
        df = df[df['containerType'] == "order"]
        df['ident'] = [str(i).split("_")[-1] for i in list(df['group'])]
        order_runs = dict()

        for order in list(df['ident'].unique()):
            tmp = df[df['ident'] == order]
            runs = []

            wrapper = auth_utils.token_response_to_bfabric(tdata)

            try:
                ress = wrapper.read_object("sample", {"tubeid":list(tmp['tubeID']),"includeruns":True,"type":"Library on Run - Illumina"})
            except:
                ress = []

            if type(ress) != type(None):
            
                for res in ress:
                    if hasattr(res, "run"):
                        for w in res.run:
                            try:
                                runs.append(w._id)
                            except:
                                pass
                    else: 
                        print("No run attribute for sample "+str(res._id))

            runs = list(set(runs))
            iseqs = dict()

            for run in runs:
                res = wrapper.read_object("run", {"id":str(run)})
                # res = tdata['bfabric_wrapper'].read_object("run", {"id":str(run)})
                if "iseq" in str(res[0].instrument).lower() or str(res[0].qc) == "true":
                    iseqs[str(run)]=res[0].name

            order_runs[order] = iseqs.copy()

        send = [
            html.Div(
                [   
                    html.P(
                        "Order "+str(order),
                        style={
                            "font-size":"14px",
                            "margin-bottom":"1px",
                        }
                    ),
                    dcc.Dropdown(
                        id="order_"+str(order),
                        options=[
                            {
                                "label": order_runs[order][elt],
                                "value": elt
                            } for elt in order_runs[order]
                            ],
                        clearable=False,
                        searchable=False,
                        value="",
                        style={"padding":"2px"}
                    ),
                ],
                style={"margin-bottom":"10px"}
            ) for order in order_runs
        ]
        # send.append(html.Button('Submit iSeq Selections', id='submit_iseq', n_clicks=0))
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
        State("bug-description", "value")
    ]
)
def submit_bug_report(n_clicks, token, entity_data, bug_description):

    if token: 
        token_data = json.loads(auth_utils.token_to_data(token))
    else:
        token_data = ""

    if n_clicks:
        try:
            sending_result = auth_utils.send_bug_report(
                token_data=token_data,
                entity_data=entity_data,
                description=bug_description
            )
            if sending_result:
                return True, False
            else:
                return False, True
        except:
            return False, True

    return False, False


@app.callback(output=[
        Output("input_df", "data"),
        Output("submit_iseq", "disabled"),
    ],
              inputs=[Input("load-val-2", "n_clicks")],
                state=[State("token", "data"),
                     State("pool_vol", "value")],prevent_initial_call=True)
def generate_input_df(start, token, pool_vol):

    tdata = json.loads(auth_utils.token_to_data(token))
    plate = tdata['entity_id_data']

    wrapper = auth_utils.token_response_to_bfabric(tdata)

    df = fns.get_plate_details(plate, pool_vol, wrapper)

    return df.to_dict("records"), False


@app.callback(output=Output("div-graphs-myra", "children"),
              inputs=[Input("input_df","data"),
                      Input('submit_iseq', 'n_clicks')],
              state=[State("dropdown-select-file-type","value"),
                    State("mal-card","children"),
                    State("pool_vol","value"),
                    State("token","data")],prevent_initial_call=True)
def generate_table(data, iseq_submit, dropdown, card, pool_vol, token):

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
        df = fns.RePool(data,orderRun,pool_vol,wrapper)

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

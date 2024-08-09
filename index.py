from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc
import dash
import dash_table
import json
import os
import bfabric
import pandas as pd
from dash import callback_context as ctx
from utils import auth_utils, components, formatting_functions as fns

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
                                            'B-Fabric App Template',
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
                        html.Div(
                            children=[html.P(id="page-title",children=[str("Bfabric App Template")], style={"font-size":"40px", "margin-left":"20px", "margin-top":"10px"})],
                            style={"margin-top":"0px", "min-height":"80px","height":"6vh","border-bottom":"2px solid #d4d7d9"}
                        )
                    )
                ),
                dbc.Row(
                    id="page-content-main",
                    children=[
                        dbc.Col(
                            html.Div(
                                id="sidebar",
                                children=components.myra_sidebar,
                                style={"border-right": "2px solid #d4d7d9", "height": "100%", "padding": "20px", "font-size": "20px"}
                            ),
                            width=3,
                        ),
                        dbc.Col(
                            html.Div(
                                id="page-content",
                                children=components.no_auth + [html.Div(id="auth-div")],style={"margin-top":"20vh", "margin-left":"2vw", "font-size":"20px"},
                            ),
                            width=9,
                        ),
                    ],
                    style={"margin-top": "0px", "min-height": "40vh"}
                ),
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
        Output('sidebar_text', 'hidden'),
        Output('example-slider', 'disabled'),
        Output('example-dropdown', 'disabled'),
        Output('example-input', 'disabled'),
        Output('example-button', 'disabled'),
    ],
    [
        Input('url', 'search'),
    ]
)
def display_page(url_params):
    
    base_title = "Bfabric App Template"

    if not url_params:
        return None, None, None, components.no_auth, base_title, True, True, True, True, True
    
    token = "".join(url_params.split('token=')[1:])
    tdata_raw = auth_utils.token_to_data(token)
    
    if tdata_raw:
        if tdata_raw == "EXPIRED":
            return None, None, None, components.expired, base_title, True, True, True, True, True

        else: 
            tdata = json.loads(tdata_raw)
    else:
        return None, None, None, components.no_auth, base_title, True, True, True, True, True
    
    if tdata:
        entity_data = json.loads(auth_utils.entity_data(tdata))
        page_title = f"{base_title} - {tdata['entityClass_data']} - {tdata['entity_id_data']} ({tdata['environment']} System)" if tdata else "Bfabric App Interface"

        if not tdata:
            return token, None, None, components.no_auth, page_title, True, True, True, True, True
        
        elif not entity_data:
            return token, None, None, components.no_entity, page_title, True, True, True, True, True
        
        else:
            if not DEV:
                return token, tdata, entity_data, components.auth, page_title, False, False, False, False, False
            else: 
                return token, tdata, entity_data, components.dev, page_title, True, True, True, True, True
    else: 
        return None, None, None, components.no_auth, base_title, True, True, True, True, True
    
@app.callback(
    Output('auth-div', 'children'),
    [
        Input('example-slider', 'value'),
        Input('example-dropdown', 'value'),
        Input('example-input', 'value'),
        Input('example-button', 'n_clicks')
    ],
    [
        State('entity', 'data'),
        State('token_data', 'data'),
    ]
)
def update_auth_div(slider_val, dropdown_val, input_val, n_clicks, entity_data, token_data):

    if not entity_data or not token_data:
        return None

    entity_details = [
        html.H1(f"Entity Data:  "),
        html.P(f"Entity Class: {token_data['entityClass_data']}"),
        html.P(f"Entity ID: {token_data['entity_id_data']}"),
        html.P(f"Created By: {entity_data['createdby']}"),
        html.P(f"Created: {entity_data['created']}"),
        html.P(f"Modified: {entity_data['modified']}"),
    ]

    output = dbc.Row(
        [
            dbc.Col(
                [
                    html.H1("Component Data: "),
                    html.P(f"Slider Value: {slider_val}"),
                    html.P(f"Dropdown Value: {dropdown_val}"),
                    html.P(f"Input Value: {input_val}"),
                    html.P(f"Button Clicks: {n_clicks}")
                ]
            ),
            dbc.Col(
                entity_details
            )
        ]
    )

    return output


@app.callback(output=Output("mal-card", "children"),
              state=[State("dropdown-select-file-type", "value"),
                     State("token", "data")],
              inputs=[Input("input_df","data")])
def generate_iseq_selectors(data, ftype, token):

    tdata = auth_utils.token_to_data(token)
    print("FTYPE:")
    print(ftype)
    if ftype == "repool":
        df = pd.DataFrame(data)
        df = df[df['containerType'] == "order"]

        df['ident'] = [str(i).split("_")[-1] for i in list(df['group'])]
        # print("ONE")
        # print([str(i).split("_")[-1] for i in list(df['group'])])

        order_runs = dict()

        for order in list(df['ident'].unique()):
            tmp = df[df['ident'] == order]
            # print("TWO")
            # print(tmp)
            runs = []

            # ress = fns.read_bfabric(endpoint="sample", obj={"tubeid":list(tmp['tubeID']),"type":"Library on Run - Illumina"}) # NOT GETTING ALL RUNS BECAUSE NEED TO PAGE THIS QUERY
            # print(list(tmp['tubeID']))
            print(tmp)
            print(list(tmp['tubeID']))
            new_wrapper = bfabric.Bfabric()
            try:
                ress = tdata['bfabric_wrapper'].read_object("sample", {"tubeid":list(tmp['tubeID']),"includeruns":True,"type":"Library on Run - Illumina"})
            except:
                ress = []
            #B = bfabric.Bfabric()
            #ress = tdata['bfabric_wrapper'].read_object(endpoint="sample", obj={"tubeid":['34224/1#4', '34224/1#3', '34224/1#13', '34224/1#2', '34224/1#11', '34224/1#10', '34224/1#7', '34224/1#6', '34224/1#5'], "type":"Library on Run - Illumina","includeruns":True})

            # ress = B.read_object("sample", {"tubeid":list(tmp['tubeID']),"type":"Library on Run - Illumina"})
            if type(ress) != type(None):
            
                for res in ress:

                    # print(res.run[0])
                    print(res)

                    if hasattr(res, "run"):
                        for w in res.run:
                            try:
                                # print("ASDF")
                                # print(w)
                                runs.append(w._id)
                            except:
                                pass
                    else: 
                        print("No run attribute for sample "+str(res._id))

            runs = list(set(runs))
            # print("RUNS:")
            # print(runs)

            iseqs = dict()
            print("RUNS:")
            print(runs)
            for run in runs:
                # res = fns.read_bfabric(endpoint="run", obj={"id":str(run)})
                res = tdata['bfabric_wrapper'].read_object("run", {"id":str(run)})
                print(run)
                if "iseq" in str(res[0].instrument).lower() or str(res[0].qc) == "true":
                    iseqs[str(run)]=res[0].name

            order_runs[order] = iseqs.copy()
        # print(runs)
        # print(iseqs)
        # print(order_runs)
        send = [dcc.Dropdown(
            id="order"+str(order),
            options=[
                {
                    "label": order_runs[order][elt],
                    "value": elt
                } for elt in order_runs[order]
                ],
            clearable=False,
            searchable=False,
            value="",
        ) for order in order_runs]
        send.append(html.Button('Submit iSeq Selections', id='submit_iseq', n_clicks=0, style={"font-size":"20px", "margin-top":"10px", "height":"40px"}))
        # send.append(html.Button('Submit iSeq Selections', id='submit_iseq', n_clicks=0, style={'color':'white'}))
        return send
    else:
        # return [html.Button('Submit iSeq Selections', id='submit_iseq', n_clicks=0, style={'color':'white'})]
        return [html.Button('Submit iSeq Selections', id='submit_iseq', n_clicks=0)]


@app.callback(output=Output("input_df", "data"),
              inputs=[Input("load-val-2", "n_clicks")],
            #   state=[State("plate_input", "value"),
                state=[State("token", "data"),
                     State("pool_vol", "value")],prevent_initial_call=True)
def generate_input_df(start, token, pool_vol):

    tdata = auth_utils.token_to_data(token)
    plate = tdata['entity_id_data']

    df = fns.get_plate_details(plate, pool_vol, tdata['bfabric_wrapper'])

    return df.to_dict("records")


@app.callback(output=Output("div-graphs-myra", "children"),
              inputs=[Input("input_df","data"),
                      Input('submit_iseq', 'n_clicks')],
              state=[State("dropdown-select-file-type","value"),
                    State("mal-card","children"),
                    State("pool_vol","value"),
                    State("token","data")],prevent_initial_call=True)
def generate_table(data, iseq_submit, dropdown, card, pool_vol, token):

    button_clicked = ctx.triggered_id

    if not data:
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
        for elt in card:
            # if True:
            try:
                # print(elt)
                # print(elt['props']['children'][0]['props']['children'].split(" ")[-1][:-1])
                # print(elt['props']['children'][1]['props']['value'])
                orderRun[elt['props']['children'][0]['props']['children'].split(" ")[-1][:-1]] = elt['props']['children'][1]['props']['value']

            except:
                # pass
                pass
        if orderRun == dict():
            return
        # print(data)
        # print(orderRun)
        # print(pool_vol)
        wrapper = auth_utils.token_to_data(token)['bfabric_wrapper']
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
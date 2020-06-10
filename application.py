import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
from functions import upload_parsing

# link fontawesome to get the chevron icons
FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FA])
app.config.suppress_callback_exceptions = True

# dff = pd.read_csv('.\data\gavia_bloom_targets Tuesday, 03. December 2019 02_49PM(1).csv', encoding ='latin1')
# dff = dff[dff["name"] == 'Groupe Canam inc']
# dff['ensemble_pred_prob'] = dff['ensemble_pred_prob'].apply(lambda x: int(x*100))

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "color": '#fefdfa',
    "background-color": "#222d32",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

upload_component = dcc.Upload(
    id='upload-data',
    children=html.Div([
        'Drag & Drop or ',
        html.A('Select CSV File')
    ]),
    style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
    },
    # Allow multiple files to be uploaded
    multiple=True,
)

sidebar = html.Div(
    [
        html.H2("META", className="display-5"),
        html.Hr(style={'border': '1px solid #3c8dbc'}),
        html.P('Micro Enforcement Targeting Algorithm'),
        html.P(
            "Upload data and generate maplots in real time", className="lead pt-2"
        ),
        upload_component,
        html.Div(id='filename_data', className='pt-5'),
        html.Div(id='last_modified_date', className='pt-2')
    ],
    style=SIDEBAR_STYLE,
    id="sidebar",
)

dropdown_row = dbc.Row([
    dbc.Col(html.Div(id='dropdown_info_div'), width=9),
    dbc.Col(html.Div(id='dropdown_score_div'))
], className='m-1')

plot_hist_table = dbc.Row(
    [
        dbc.Col(dcc.Loading(dcc.Graph(id='compliance_histogram',
                                      config={'displayModeBar': False}
                                      )), width=5),
        dbc.Col(dcc.Loading(id='table_div'), width=7)
    ],
    no_gutters=True, className='row-first'
)

plots_map = dbc.Row(
    [
        dbc.Col(dcc.Loading(html.Div(id='div_graph')))
    ],
    no_gutters=True
)

content = html.Div([
    dcc.Store(id='data_json'),
    dropdown_row,
    plots_map,
    plot_hist_table,
], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])


# @app.callback(
#     [Output('name', 'children'),
#      Output('date', 'children'),
#      # Output('data', 'data')
#      ],
#     [Input('upload-data', 'contents')],
#     [State('upload-data', 'filename'),
#      State('upload-data', 'last_modified')])
# def update_output(list_of_contents, list_of_names, list_of_dates):
#     if list_of_contents is not None:
#         children = [
#             upload_parsing.parse_contents(c, n, d) for c, n, d in
#             zip(list_of_contents, list_of_names, list_of_dates)]
#         return str(children)

@app.callback(
    [Output('filename_data', 'children'),
     Output('last_modified_date', 'children'),
     Output('dropdown_info_div', 'children'),
     Output('dropdown_score_div', 'children'),
     Output('data_json', 'data')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        for c, n, d in zip(list_of_contents, list_of_names, list_of_dates):
            # file_name, date, child1, child2, data = upload_parsing.parse_contents(c, n, d)
            return upload_parsing.parse_contents(c, n, d)

    else:
        raise dash.exceptions.PreventUpdate()


@app.callback(
    Output('div_graph', 'children'),
    [Input('data_json', 'data'),
     Input('dropdown_info', 'value'),
     Input('dropdown_score', 'value')])
def show_table(data, data_show, score):
    if data is not None:
        dff = pd.read_json(data)
        return upload_parsing.generate_figure(dff, data_show, score)
    else:
        raise dash.exceptions.PreventUpdate()


@app.callback(
    Output('compliance_histogram', 'figure'),
    [Input('data_json', 'data'),
     # Input('dropdown_info', 'value'),
     Input('dropdown_score', 'value'),
     # Input('dropdown_company', 'value')
     ])
def return_histogram(data, score):
    dff = pd.read_json(data)
    if score:
        return upload_parsing.return_histogram(dff, score)


@app.callback(
    Output('table_div', 'children'),
    [Input('compliance_histogram', 'clickData'),
     Input('dropdown_score', 'value')],
    [State('data_json', 'data')]
)
def update_table(clickdata, score, data):
    dff = pd.read_json(data)
    if clickdata is None:
        return upload_parsing.generate_table(dff, score)
    else:
        hovered_points = clickdata['points'][0]['pointNumbers']
        dff = dff.iloc[hovered_points]
    return upload_parsing.generate_table(dff, score)


if __name__ == "__main__":
    app.run_server(debug=True)

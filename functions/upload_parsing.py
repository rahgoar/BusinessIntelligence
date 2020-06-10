import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
import plotly.express as px
import plotly.graph_objects as go
from credentials import credentials

import pandas as pd


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    dff = df.to_json()
    # Dropdown
    dff_columns = df.columns.to_list()

    dropdown_info = dbc.FormGroup(
        [
            dcc.Dropdown(id='dropdown_info',
                         options=[{'label': x, 'value': x} for x in dff_columns],
                         value=["address", "days_since_last_visit"],
                         multi=True
                         ),
            dbc.FormText(
                "Select Labels which you want to show on plot..",
                color="secondary",
                className='ml-1'
            )
        ]
    )

    dropdown_score = dbc.FormGroup(
        [
            dcc.Dropdown(id='dropdown_score',
                         options=[{'label': x, 'value': x} for x in dff_columns],
                         value='ensemble_pred_prob',
                         clearable=False
                         ),
            dbc.FormText(
                "Score Column..",
                color="secondary",
                className='ml-1'
            )
        ]
    )

    return 'Uploaded filename: {}'.format(filename), \
           'Last modified on: {}'.format(datetime.datetime.fromtimestamp(date)), \
           dropdown_info, dropdown_score, dff


def generate_figure(dff, data_show, score):
    dff[score] = dff[score].apply(lambda x: x * 100)

    px.set_mapbox_access_token(credentials['MapBox_Token'])
    fig = px.scatter_mapbox(dff, lat="latitude", lon="longitude", hover_name="name",
                            hover_data=data_show,
                            color=score,
                            color_continuous_scale=px.colors.cyclical.IceFire,
                            height=500,
                            size_max=10)

    fig.update_layout(
        # title="Carlos's Machine Learning Predictions",
        autosize=True,
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            accesstoken=credentials['MapBox_Token'],
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=54,
                lon=-96,

            ),
            pitch=0,
            zoom=3,
            style='light'
        ),
    )
    fig.update_layout(margin={"t": 25, "b": 20})
    return dcc.Graph(figure=fig)


def return_histogram(dff, score):
    dff[score] = dff[score].apply(lambda x: x * 100)
    data = go.Histogram(
        x=dff[score],
        marker_color="#abb1cf",
        marker={"line": {
            "color": "black",
            "width": 0.2,
        }}
    )
    plot = {
        'data': [data],
        'layout': {
            # 'title': "Distribution of Regulations by Years Since Last Modified",
            "xaxis": {
                "title": {
                    "text": "Non compliance prediction %"
                }
            },
            "yaxis": {
                "title": "Number of Companies"
            },
            'font': {
                'family': "-apple-system, BlinkMacSystemFont, sans-serif",
            },
            'margin': {"t": 0},
        }
    }

    return plot


def generate_table(dff, score):
    dff = dff[['name', score]].copy()
    # dff[score] = dff[score].apply(lambda x: x * 100)
    dff[score] = (dff[score]).apply('{:.2%}'.format)

    # Sorting
    dff = dff.sort_values(by=[score], ascending=False)
    datatable = dt.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in dff.columns],
        # columns=[{"name": 'Company name', "id": "name"},
        #          {"name": 'Score', "id": score}],

        data=dff.to_dict('records'),
        style_cell={
            'textAlign': 'left',
            'fontSize': '0.8rem',
            'font-family': 'sans-serif',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': 0,
        },
        style_table={
            'maxHeight': '400px',
            'overflowY': 'scroll',
            # 'border': 'thin lightgrey solid'
        },
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        style_cell_conditional=[
            {
                'if': {'column_id': 'name'},
                'padding-left': '10px'
            },
            {
                'if': {'column_id': score},
                'textAlign': 'center',
                'width': '20%'
            },
        ],
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            },
            {
                'if': {'column_id': score},
                'backgroundColor': '#c5b9cd',
                'color': 'black',
            },
            # {
            #     'if': {'column_id': 'Department'},
            #     'backgroundColor': '#146eb4',
            #     'color': 'white',
            # },
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_as_list_view=True,

    )

    return datatable

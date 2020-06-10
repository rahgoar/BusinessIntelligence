# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
#
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#
# app.layout = html.Div([
#     dcc.Input(id='my-id', value='initial value', type='text'),
#     html.Div(id='my-div')
# ])
#
#
# @app.callback(
#     Output('my-div', 'children'),
#     [Input('my-id', 'value')]
# )
# def update_output_div(input_value):
#     return 'You\'ve entered "{}"'.format(input_value)
#
#
# if __name__ == '__main__':
#     app.run_server(debug=True)


# 2-------Plotly Return------

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Store(id="my-id"),
    dcc.Graph(id='my-div')
])


@app.callback(
    Output('my-div', 'figure'),
    [Input('my-id', 'value')]
)
def update_output_div(input_value):
    df = px.data.gapminder().query("country=='Canada'")
    fig = px.line(df, x="year", y="lifeExp", title='Life expectancy in Canada')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

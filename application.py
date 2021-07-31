import json
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px


df_test = px.data.iris()


with open('area_catastral_lotes.json') as f:
    zones = json.load(f)


i = 1
list_lots = []
for feature in zones["features"]:
    feature['id'] = str(i).zfill(6)
    list_lots.append(feature['id'])
    i += 1


data_pol = pd.DataFrame(list_lots, columns=['lot_id'])
data_pol['color'] = 12


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1('Rural maps exploration'),
    dbc.Row([dbc.Col([html.Label("Lot label:"),
                      dcc.Input(
                          id='lot_label',
                          placeholder='Enter the lot id',
                          value=''
                      )], width=3),
             dbc.Col(dcc.Dropdown(id='layer',
                                  options=[{'label': 'Lots division', 'value': 'boundaries'}],
                                  value='boundaries'),width=9)]),
    dbc.Row([dbc.Col(dcc.Dropdown(id='activity', options=[{'label': 'Dummy_activity',
                                                           'value': 'dummy'}], multi=True, value='dummy'), width=3),
             dbc.Col(dcc.Graph(id='choropleth'), width=9)]),
    dbc.Row([dbc.Col([dcc.Dropdown(id='variable',
                                   options=[{'label': 'Closeness to water', 'value': 'water_c'}],
                                   value='water_c')], width=3),
             dbc.Col(dcc.Graph(id='scatter'), width=9)])
])

@app.callback(
    Output('choropleth', 'figure'),
    Input('lot_label', 'value'),
    Input('layer', 'value'))
def display_choropleth(lot_label, layer):
    if lot_label:
        temp = data_pol[data_pol['lot_id'] == lot_label]
        coords_df = pd.DataFrame(zones['features'][int(lot_label)]['geometry']['coordinates'][0], columns=['longitude', 'latitude'])
        coordinates = coords_df.mean(axis=0)
        fig = px.choropleth_mapbox(
            temp, geojson=zones, color='color',
            locations='lot_id',
            #zoom=15, center={"lat": coordinates[1] - 0.3285, "lon": coordinates[0] - 0.2175},
            #zoom=15, center={"lat": coordinates[1], "lon": coordinates[0]},
            zoom=9, center={"lat": 4.2110, "lon": -74.0721},
            mapbox_style="carto-positron",
            range_color=[0, 12])
        fig.update_geos(fitbounds="locations")
        fig.update_layout(height=800)
        return fig
    else:
        fig = px.choropleth_mapbox(
            data_pol, geojson=zones, color='color',
            locations='lot_id',
            zoom=9, center={"lat": 4.2110, "lon": -74.0721},
            mapbox_style="carto-positron",
            range_color=[0, 12])
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=800)
        return fig


@app.callback(
    Output('scatter', 'figure'),
    Input('variable', 'value'))
def update_scatter(variable):
    fig = px.scatter(df_test, x="sepal_width", y="sepal_length", color="species",
                     size='petal_length', hover_data=['petal_width'])
    return fig


app.run_server(debug=True)

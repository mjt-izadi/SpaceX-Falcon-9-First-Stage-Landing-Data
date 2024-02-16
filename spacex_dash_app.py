import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

site_dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in spacex_df['Launch Site'].unique():
    site_dropdown_options.append({'label': site, 'value': site})

range_slider_marksdict = dict()
for i in range(0, 10000, 1000):
    range_slider_marksdict[i] = str(i)

app = dash.Dash(__name__)

app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                dcc.Dropdown(id='site-dropdown',
                                             options=site_dropdown_options,
                                             value='ALL',
                                             placeholder='Select a Launch Site here',
                                             searchable=True),
                                html.Br(),
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks=range_slider_marksdict,
                                                value=[min_payload, max_payload]),
                                html.Div(dcc.Graph(id='success-payload-scatter-chart'))])

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        data = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(data, values='class', names='Launch Site',
                     title='Total Successful Launches Count for All Sites')
    else:
        data = spacex_df[spacex_df['Launch Site']==entered_site]['class'].value_counts()
        fig = px.pie(data, values='count',
                     names=['Success' if i==1 else 'Fail' for i in data.index],
                     title='Site %s Launches'%entered_site)
    return(fig)

@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])

def get_scatter_chart(entered_site, entered_payload_range):
    data = spacex_df[spacex_df['Payload Mass (kg)']>=entered_payload_range[0]]
    data = data[data['Payload Mass (kg)']<=entered_payload_range[1]]
    if entered_site == 'ALL':
        fig = px.scatter(data, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title='Correlation between Payload Mass and Success for All Sites')
    else:
        data = data[data['Launch Site']==entered_site]
        fig = px.scatter(data, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title='Correlation between Payload Mass and Success for Site %s'%entered_site)
    return(fig)

if __name__ == '__main__':
    app.run_server()

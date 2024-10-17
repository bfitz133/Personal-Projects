# Import required libraries
import io # type: ignore
import json # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import dash # type: ignore
from dash import html # type: ignore
from dash import dcc # type: ignore
from dash.dependencies import Input, Output, State # type: ignore
import plotly.express as px # type: ignore
import pybaseball as base # type: ignore
import dash_bootstrap_components as dbc # type: ignore
base.cache.enable()

# Create a dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SIMPLEX])

# Create an app layout
app.layout = dbc.Container(html.Div(children=[html.H1('MLB Batting Dashboard',
                                        style={'textAlign': 'center', 'color': '#ffffff',
                                               'font-size': 40}),
                                              dcc.Dropdown(id='year-dropdown',
                                                           options=[{'label': '2021', 'value': 2021},
                                                                    {'label': '2022', 'value': 2022},
                                                                    {'label': '2023', 'value': 2023},
                                                                    {'label': '2024', 'value': 2024}],
                                                           value=2024,
                                                           placeholder='Select Year Here',
                                                           searchable=True,
                                                           style={'backgroundColor': '#EDEDED'}),
                                  dcc.Dropdown(id='player-dropdown', 
                                  options=[],
                                  value='Shohei Ohtani',
                                  placeholder="Select an MLB Player Here",
                                  searchable=True,
                                  style={'backgroundColor': '#EDEDED'}),
                                  dcc.Store(id='intermediate-value', storage_type='session'),
                                html.Br(),
                                dbc.Row([dbc.Col(dbc.Card(id='batting_average_card', style = {"width": "12.5rem"}), width='auto'),
                                dbc.Col(dbc.Card(id='runs_card', style = {"width": "12.5rem"}), width='auto'),         
                                dbc.Col(dbc.Card(id='home_runs_card', style = {"width": "12.5rem"}), width='auto'),
                                dbc.Col(dbc.Card(id='rbi_card', style = {"width": "12.5rem"}), width='auto'),
                                dbc.Col(dbc.Card(id='ops_card', style = {"width": "12.5rem"}), width='auto')]),
                                html.Br(),
                                dcc.Dropdown(id='statistic-dropdown',
                                             options=[{'label': 'Batting Average', 'value': 'Batting Average'},
                                                      {'label': 'Home Runs', 'value': 'Home Runs'}],
                                             value='Batting Average', placeholder='Choose Statistic Here',
                                             searchable=True,
                                             style={'backgroundColor': '#EDEDED'}),
                                dbc.Row([dbc.Col(html.Br()),
                                html.Div(dcc.Graph(id='BA-BAR', figure={'layout': {'height': 300}}))])
                                         ])
                                
, className='dashboard-container')
    

# Callback Function for Year Selection
@app.callback(Output(component_id='player-dropdown', component_property='options'),
              Output('intermediate-value','data'),
              Input(component_id='year-dropdown', component_property='value'))

def set_year(chosen_year):
    current_batting = base.batting_stats_bref(chosen_year)
    df_mlbid = current_batting['mlbID']
    current_batting['Year'] = chosen_year
    current_batting['mlbID2'] = current_batting['mlbID']
    current_batting = current_batting.set_index('mlbID')


    # create list of dictionaries (key value pairs) of the players name to be used in the dropdown
    players = current_batting['Name']
    players_dict = players.to_dict()


    dropdown_dict = {}
    dropdown_list = []
    for player in players_dict.values():
        dropdown_dict['label'] = player
        dropdown_dict['value'] = player
        dropdown_list.append(dropdown_dict)
        dropdown_dict = {}
    return dropdown_list, current_batting.to_json(date_format='iso', orient='split')
    
# Callback Function for Batting Visuals
@app.callback(Output(component_id='batting_average_card', component_property='children'),
              Output(component_id='runs_card', component_property='children'),
              Output(component_id='home_runs_card', component_property='children'),
              Output(component_id='rbi_card', component_property='children'),
              Output(component_id='ops_card', component_property='children'),
              Output(component_id='BA-BAR', component_property='figure'),
              Input(component_id='player-dropdown', component_property='value'),
              Input(component_id='statistic-dropdown', component_property='value'),
              Input('intermediate-value', 'data'))

def get_card_viz(player, statistic, batting):
    #filter for selected player
    current_batting = pd.read_json(io.StringIO(batting), orient='split')
    selected_player = current_batting[current_batting['Name'] == player]
    year = int(current_batting['Year'].iloc[0])
    
    #batting average
    ba = float(selected_player['BA'].iloc[0])
    ba_card = dbc.Card([dbc.CardHeader('Batting Average'), dbc.CardBody([html.H4(f"{ba:.3f}", className='card-value')])],
             style = {"width": "12.5rem"}, class_name='card', inverse=True)
    
    #runs scored
    runs_card = dbc.Card([dbc.CardHeader('Runs'), dbc.CardBody([html.H4(selected_player['R'], className='card-value')])],
             style = {"width": "12.5rem"}, class_name='card', inverse=True)
    
    #home runs
    hr_card = dbc.Card([dbc.CardHeader('Home Runs'), dbc.CardBody([html.H4(selected_player['HR'], className='card-value')])],
             style = {"width": "12.5rem"}, class_name='card', inverse=True)
    
    #runs batted in
    rbi_card = dbc.Card([dbc.CardHeader('RBI'), dbc.CardBody([html.H4(selected_player['RBI'], className='card-value')])],
             style = {"width": "12.5rem"}, class_name='card', inverse=True)
    
    #ops
    ops = float(selected_player['OPS'].iloc[0])
    ops_card = dbc.Card([dbc.CardHeader('OPS'), dbc.CardBody([html.H4(f"{ops:.3f}", className='card-value')])],
             style = {"width": "12.5rem"}, class_name='card', inverse=True)
    
    #statcast data
    dates_dict = {2021: ['2021-04-01', '2021-10-03'],
                  2022: ['2022-03-31', '2022-10-02'],
                  2023: ['2023-03-30', '2023-10-01'],
                  2024: ['2024-03-20', '2024-09-30']}
    
    statcast_player = base.statcast_batter(start_dt=dates_dict[year][0],
                                           end_dt=dates_dict[year][1],
                                           player_id=selected_player['mlbID2'].iloc[0])
    
    #drop nulls
    statcast_player = statcast_player.dropna(how='all', axis=0)
    
    #add month call for further analysis
    statcast_player['Month'] = pd.to_datetime(statcast_player['game_date']).dt.month
    statcast_player['Hit'] = statcast_player['events'].apply(lambda x: 1 if x in ['single', 'double', 'triple', 'home_run'] else 0)
    
    #drop nulls in events
    statcast_player = statcast_player.dropna(axis=0, subset=['events'])
    
    def f(row):
        if row['events'] in ['single', 'double', 'triple', 'home_run']:
            val = 1
        elif row['events'].__contains__('out'):
            val = 1
        elif row['events'].__contains__('error'):
            val = 1
        else:
            val = 0
        return val

    statcast_player['At Bats'] = statcast_player.apply(f, axis=1)
    
    #monthly statistic graph
    
    #batting average
    statcast_ba = statcast_player[['Month','Hit', 'At Bats']].groupby(['Month']).sum()
    statcast_ba['BA'] = statcast_ba['Hit']/statcast_ba['At Bats']
    statcast_ba = statcast_ba.reset_index()
    pd.options.display.float_format = '{:.3f}'.format
    
    #home runs
    statcast_hr = statcast_player[statcast_player['events'] == 'home_run']

    statcast_hr_count = statcast_hr[['Month','Hit']].groupby(['Month']).sum()
    statcast_hr_count = statcast_hr_count.reset_index()
    
    if statistic == 'Batting Average':
        x_val = statcast_ba['Month']
        y_val = statcast_ba['BA']
        title_val = 'Batting Average by Month'
        y_label = 'Batting Average'
    else:
        x_val = statcast_hr_count['Month']
        y_val = statcast_hr_count['Hit']
        title_val = 'Home Runs by Month'
        y_label = 'Home Runs'
   
    fig = px.bar(x=x_val, y=y_val, text = y_val,
                 title=title_val, labels={'x': 'Month', 'y': y_label},
                color=y_val, color_continuous_scale=['orange', 'yellow', 'green'])
    if statistic == 'Batting Average':
        fig.update_traces(texttemplate = '%{text:.3f}', textposition='inside', insidetextanchor='end', name=y_label)
    fig.add_scatter(x=x_val, y=y_val, mode='lines', name=y_label,
                    marker=dict(color='white'), showlegend=False)
    #fig.layout.template = 'plotly_dark'
    fig.layout.plot_bgcolor = '#323232'
    fig.layout.paper_bgcolor = '#323232'
    fig.layout.font = {'color': '#FFFFFF'}
    return ba_card, runs_card, hr_card, rbi_card, ops_card, fig

if __name__ == '__main__':
    app.run_server()


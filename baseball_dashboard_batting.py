# Import required libraries

import pandas as pd # type: ignore
import dash # type: ignore
from dash import html # type: ignore
from dash import dcc # type: ignore
from dash.dependencies import Input, Output # type: ignore
import plotly.express as px # type: ignore
import pybaseball as base # type: ignore
import dash_bootstrap_components as dbc # type: ignore

current_batting = base.batting_stats_bref(2024)
df_mlbid = current_batting['mlbID']
current_batting = current_batting.set_index('mlbID')

# Create a dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SIMPLEX])


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
    
# Create an app layout
app.layout = dbc.Container(html.Div(children=[html.H1('MLB Batting Dashboard',
                                        style={'textAlign': 'center', 'color': '#ffffff',
                                               'font-size': 40}),
                                # Add a dropdown list to select the team
                                # The default select value is for ALL sites
                                  dcc.Dropdown(id='player-dropdown', 
                                  options=dropdown_list,
                                  value='Shohei Ohtani',
                                  placeholder="Select an MLB Player Here",
                                  searchable=True),
                                html.Br(),
                                dbc.Row([dbc.Col(dbc.Card(id='batting_average_card', style = {"width": "12.5rem"}), width='auto'),
                                dbc.Col(dbc.Card(id='runs_card', style = {"width": "12.5rem"}), width='auto'),         
                                dbc.Col(dbc.Card(id='home_runs_card', style = {"width": "12.5rem"}), width='auto'),
                                dbc.Col(dbc.Card(id='rbi_card', style = {"width": "12.5rem"}), width='auto'),
                                dbc.Col(dbc.Card(id='ops_card', style = {"width": "12.5rem"}), width='auto')])
                                
                                


]), className='dashboard-container')

# Callback Function for Batting Average Card
@app.callback(Output(component_id='batting_average_card', component_property='children'),
              Output(component_id='runs_card', component_property='children'),
              Output(component_id='home_runs_card', component_property='children'),
              Output(component_id='rbi_card', component_property='children'),
              Output(component_id='ops_card', component_property='children'),
              Input(component_id='player-dropdown', component_property='value'))

def get_card_viz(player):
    #filter for selected player
    selected_player = current_batting[current_batting['Name'] == player]
    
    #batting average
    ba = float(selected_player['BA'].iloc[0])
    ba_card = dbc.Card([dbc.CardHeader('Batting Average'), dbc.CardBody([html.H4(f"{ba:.3f}", className='card-value')])],
             style = {"width": "12.5rem"})
    
    #runs scored
    runs_card = dbc.Card([dbc.CardHeader('Runs'), dbc.CardBody([html.H4(selected_player['R'], className='card-value')])],
             style = {"width": "12.5rem"})
    
    #home runs
    hr_card = dbc.Card([dbc.CardHeader('Home Runs'), dbc.CardBody([html.H4(selected_player['HR'], className='card-value')])],
             style = {"width": "12.5rem"})
    
    #runs batted in
    rbi_card = dbc.Card([dbc.CardHeader('RBI'), dbc.CardBody([html.H4(selected_player['RBI'], className='card-value')])],
             style = {"width": "12.5rem"})
    
    #ops
    ops = float(selected_player['OPS'].iloc[0])
    ops_card = dbc.Card([dbc.CardHeader('OPS'), dbc.CardBody([html.H4(f"{ops:.3f}", className='card-value')])],
             style = {"width": "12.5rem"})
    return ba_card, runs_card, hr_card, rbi_card, ops_card

if __name__ == '__main__':
    app.run_server()


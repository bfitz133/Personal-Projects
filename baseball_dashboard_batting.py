# Import required libraries
import io # type: ignore
import json # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import dash # type: ignore
from dash import html # type: ignore
from dash import dcc, dash_table # type: ignore
from dash.dependencies import Input, Output, State # type: ignore
import plotly.express as px # type: ignore
import pybaseball as base # type: ignore
import dash_bootstrap_components as dbc # type: ignore
import plotly.graph_objects as go # type: ignore
from datetime import datetime
base.cache.enable()

#begin and end dates for each mlb season
dates_dict = {2021: ['2021-03-30', '2021-10-04'],
                  2022: ['2022-03-30', '2022-10-03'],
                  2023: ['2023-03-29', '2023-10-02'],
                  2024: ['2024-03-19', '2024-10-02']}
# Create a dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create an app layout
app.layout = dbc.Container(html.Div(
    children=[  html.H3('MLB Batting Dashboard',
                    style={'textAlign': 'center', 'color': '#ffffff', 'font-size': 28}),
              
                html.H4('', id='playerteam',
                    style={'textAlign': 'left', 'color': '#ffff00', 'font-size': 18}),
              
                dcc.Dropdown(id='year-dropdown',
                    options=[{'label': '2021', 'value': 2021},
                             {'label': '2022', 'value': 2022},
                             {'label': '2023', 'value': 2023},
                             {'label': '2024', 'value': 2024}],
                    value=2024,
                    placeholder='Select Year Here',
                    searchable=True,
                    style={'backgroundColor': '#FFFFFF'}),
              
                dcc.Dropdown(id='player-dropdown', 
                    options=[],
                    value='Shohei Ohtani',
                    placeholder="Select an MLB Player Here",
                    searchable=True,
                    style={'backgroundColor': '#FFFFFF'}),
                
                dcc.Store(id='intermediate-value', storage_type='session'),
                
                html.Br(),
                                
                dbc.Row([
                    dbc.Col(dbc.Card(id='batting_average_card', style = {"width": "12.5rem"}), width='auto'),
                    
                    dbc.Col(dbc.Card(id='runs_card', style = {"width": "12.5rem"}), width='auto'), 
                            
                    dbc.Col(dbc.Card(id='home_runs_card', style = {"width": "12.5rem"}), width='auto'),
                    
                    dbc.Col(dbc.Card(id='rbi_card', style = {"width": "12.5rem"}), width='auto'),
                    
                    dbc.Col(dbc.Card(id='ops_card', style = {"width": "12.5rem"}), width='auto')],
                        style={'height':85}),
                
                html.Br(), 
                
                dbc.Row([
                    dbc.Col(html.P('Select Date Range to Filter Both Visuals:   ',
                                    style={'textAlign': 'right', 'color': '#ffffff', 'font-size': 14})), 
                    
                    dbc.Col(dcc.DatePickerRange(id='my-date-picker', start_date='', 
                                                end_date='', min_date_allowed='', max_date_allowed='',
                                                style={'backgroundColor': '#FFFFFF', 'textAlign': 'center'},))],
                        
                        style={'width': '100%', 'display': 'flex', 'height': '35px', 
                               'align-items': 'center', 'justify-content': 'center'},
                        ),
                
                html.Br(), 
                    
                dbc.Row([
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody(
                                [dbc.Row([
                                    dbc.Col([
                                        html.Label(['Statistic:'], style={'font-weight':'bold', 'font-size': 11,
                                                                                                'color': '#FFFFFF'}),
                                        dcc.Dropdown(id='statistic-dropdown',
                                        options=[{'label': 'Batting Average', 'value': 'Batting Average'},
                                                 {'label': 'Home Runs', 'value': 'Home Runs'}],
                                        value='Batting Average', placeholder='Choose Statistic Here',
                                        searchable=True,
                                        style={'width': '100%', 'font-size': 10,
                                                'backgroundColor': '#FFFFFF', 'height': '25px', 'display': 'inline-block'})], width=5),
                                    dbc.Col([
                                        html.Label(['Group By:'], style={'font-weight':'bold', 'font-size': 11,
                                                                                                'color': '#FFFFFF'}),
                                        dcc.Dropdown(id='grouping',
                                        options=[{'label': 'Month', 'value': 'Month'},
                                                 {'label': 'R/L Split', 'value': 'p_throws'},
                                                 {'label': 'Pitch Type', 'value': 'pitch_name'},
                                                 {'label': 'Count', 'value': 'Batter_Count'}],
                                        value='Month', placeholder='choose grouping',
                                        style={'width': '100%', 'font-size': 10,
                                                'backgroundColor': '#FFFFFF', 'height': '25px', 'display': 'inline-block'})], width=3)
                                ]),#dbc Row just within cardbody closed
                                 
                                 
                                 
                                 
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Graph(id='BA-BAR', figure=
                                               {'layout': {'height': 255, 'width': 400}}))])]), #endcardbody
                                                                            style={'height':330})  #endcard
                                                                                    ], width = 5), #end dbc col
                    
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody(
                                [dbc.Row([
                                    dbc.Col([html.Label(['Statcast Metric:'], style={'font-weight':'bold', 'font-size': 11,
                                                                                                'color': '#FFFFFF'}),
                                        dbc.DropdownMenu(id='statcast-dropdown',
                                                         children=[dcc.Checklist(id = 'statcast-checklist', options=[{'label': 'Pitch Type', 'value': 'pitch_name'},
                                                 {'label': 'Outs', 'value': 'outs_when_up'}])], label = 'Choose StatCast Metrics', size='sm', direction = 'up',
                                                         color = '#999999',
                                        toggle_style={'border-color': '#999999', 'height': '25px', 'display': 'inline-block', 
                                                      'font-size':10, 'width': '100%'},
                                        style={'width': '100%', 'font-size': 10,
                                                'backgroundColor': '#FFFFFF', 'height': '25px', 'display': 'inline-block'})], width=6)]),
                    
                    
                    #dbc col in outer dbc row
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Graph(id='pitch-scatter', figure=
                                               {'layout': {'height': 256, 'width': 290}}, config={"frameMargins":30})), 
                                    ], style={'height':300}), ]),style={'height': 330, 'width': 310})])
                    
                , dbc.Col(dcc.Graph(id='game-grid', figure=
                                               {'layout': {'height': 330, 'width': 260}}))])
    ]
) ,className='dashboard-container')
    

# Callback Function for Year Selection
@app.callback(Output(component_id='player-dropdown', component_property='options'),
              Output('intermediate-value','data'),
              Output(component_id='my-date-picker', component_property='start_date'),
              Output(component_id='my-date-picker', component_property='end_date'),
              Output(component_id='my-date-picker', component_property='min_date_allowed'),
              Output(component_id='my-date-picker', component_property='max_date_allowed'),
              Input(component_id='year-dropdown', component_property='value'))

def set_year(chosen_year):
    current_batting = base.batting_stats_bref(chosen_year)
    current_batting['Year'] = chosen_year
    current_batting['mlbID2'] = current_batting['mlbID']
    current_batting = current_batting.set_index('mlbID')
    
    #output to use as input for dcc.datepicker
    min_game_date = dates_dict[chosen_year][0]
    max_game_date = dates_dict[chosen_year][1]


    # create list of dictionaries (key value pairs) of the players name to be used in the dropdown
    players = current_batting['Name']
    players_dict = players.to_dict()


    dropdown_dict = {}
    dropdown_list = []
    for player in players_dict.values():
        dropdown_dict['label'] = player.encode('utf-8').decode('unicode_escape').encode('latin-1').decode('utf-8')
        dropdown_dict['value'] = player
        dropdown_list.append(dropdown_dict)
        dropdown_dict = {}
    return dropdown_list, current_batting.to_json(date_format='iso', orient='split'), min_game_date, max_game_date, min_game_date, max_game_date


    
# Callback Function for Batting Visuals
@app.callback(Output(component_id='batting_average_card', component_property='children'),
              Output(component_id='runs_card', component_property='children'),
              Output(component_id='home_runs_card', component_property='children'),
              Output(component_id='rbi_card', component_property='children'),
              Output(component_id='ops_card', component_property='children'),
              Output(component_id='BA-BAR', component_property='figure'),
              Output(component_id='playerteam', component_property='children'),
              Output(component_id='game-grid', component_property='figure'),
              Output(component_id='pitch-scatter', component_property='figure'),
              Input(component_id='player-dropdown', component_property='value'),
              Input(component_id='statistic-dropdown', component_property='value'),
              Input('intermediate-value', 'data'),
              Input(component_id= 'my-date-picker', component_property='start_date'),
              Input(component_id='my-date-picker', component_property='end_date'),
              Input(component_id='grouping', component_property='value'),
              Input(component_id='statcast-dropdown', component_property='value'))

def get_card_viz(player, statistic, batting, start_date, end_date, groupon, statcast_metric):
    #filter for selected player
    current_batting = pd.read_json(io.StringIO(batting), orient='split')
    selected_player = current_batting[current_batting['Name'] == player]
    team = 'Team: ' + selected_player['Tm'].iloc[0]
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
    
    statcast_player = base.statcast_batter(start_dt=dates_dict[year][0],
                                           end_dt=dates_dict[year][1],
                                           player_id=selected_player['mlbID2'].iloc[0])
    
    #drop nulls
    statcast_player = statcast_player.dropna(how='all', axis=0)
    statcast_player = statcast_player[statcast_player['game_type'] == 'R']
    
    #date picker filtering
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    statcast_player['game_date_date'] = pd.to_datetime(statcast_player['game_date'])
    statcast_player = statcast_player[statcast_player['game_date_date'] >= start_date]
    statcast_player = statcast_player[statcast_player['game_date_date'] <= end_date]
    
    #add month, walk and hit columns for further analysis
    statcast_player['Month'] = pd.to_datetime(statcast_player['game_date']).dt.month
    statcast_player['Walk'] = statcast_player['events'].apply(lambda x: 1 if x =='walk' else 0)
    statcast_player['Hit'] = statcast_player['events'].apply(lambda x: 1 if x in ['single', 'double', 'triple', 'home_run'] else 0)
    
    
    #scatter plot for pitch result
    def g(row):
        if row['events'] in ['single', 'double', 'triple', 'home_run']:
            val = 'Hit'
        elif row['description'].__contains__('ball'):
            val = 'Ball'
        elif row['description'].__contains__('pitchout'):
            val = 'Ball'
        elif row['description'].__contains__('hit_by_pitch'):
            val = 'Ball'
        else:
            val = 'Strike'
        return val

    statcast_player['Pitch_Result_2'] = statcast_player.apply(g, axis=1)

    Strike = statcast_player[statcast_player['Pitch_Result_2'] == 'Strike']
    Ball = statcast_player[statcast_player['Pitch_Result_2'] == 'Ball'] 
    Hit = statcast_player[statcast_player['Pitch_Result_2'] == 'Hit']                 
    pitch_scatter = go.Figure()
    
    pitch_scatter.add_trace(go.Scatter(
    x=Strike['plate_x'], y=Strike['plate_z'], marker_symbol = 'x',
    name="Strike", mode= 'markers', marker_color='red', text=Strike['pitch_name']))
    
    pitch_scatter.add_trace(go.Scatter(
    x=Ball['plate_x'], y=Ball['plate_z'],
    name="Ball", mode= 'markers', marker_color='#378bf1', text=Ball['pitch_name']))
    
    pitch_scatter.add_trace(go.Scatter(
    x=Hit['plate_x'], y=Hit['plate_z'],
    name="Hit", mode= 'markers', marker_color='green', text=Hit['pitch_name']))
    
    pitch_scatter.add_trace(go.Scatter(
        x=[-.83, .83], y=[1.5, 1.5], mode='lines', marker_color='white', showlegend=False
    ))
    pitch_scatter.add_trace(go.Scatter(
        x=[-.83, .83], y=[3.5, 3.5], mode='lines', marker_color='white', showlegend=False
    ))
    pitch_scatter.add_trace(go.Scatter(
        x=[-.83, -.83], y=[1.5, 3.5], mode='lines', marker_color='white', showlegend=False
    ))
    pitch_scatter.add_trace(go.Scatter(
        x=[.83, .83], y=[1.5, 3.5], mode='lines', marker_color='white', showlegend=False
    ))
    pitch_scatter.add_trace(go.Scatter(
        x=[-.277, -.277], y=[1.5, 3.5], mode='lines', marker_color='white', showlegend=False
    ))
    pitch_scatter.add_trace(go.Scatter(
        x=[.277, .277], y=[1.5, 3.5], mode='lines', marker_color='white', showlegend=False
    ))
    pitch_scatter.add_trace(go.Scatter(
        x=[-.83, .83], y=[2.167, 2.167], mode='lines', marker_color='white', showlegend=False
    ))
    pitch_scatter.add_trace(go.Scatter(
        x=[-.83, .83], y=[2.833, 2.833], mode='lines', marker_color='white', showlegend=False
    ))
    
    
    
    
    #pitch_scatter.update_layout(showlegend=True)
    
    
    #drop nulls in events
    statcast_player = statcast_player.dropna(axis=0, subset=['events'])
    
    #create at bats column
    def f(row):
        if row['events'] in ['single', 'double', 'triple', 'home_run']:
            val = 1
        elif row['events'].__contains__('out'):
            val = 1
        elif row['events'].__contains__('error'):
            val = 1
        elif row['events'].__contains__('double_play'):
            val = 1
        elif row['events'].__contains__('fielders_choice'):
            val = 1
        else:
            val = 0
        return val

    statcast_player['At_Bats'] = statcast_player.apply(f, axis=1)
    
    #Batter_Count column
    statcast_player['Batter_Count'] = statcast_player['balls'].astype(str) + '-' + statcast_player['strikes'].astype(str)
    
    #batting average calc grouped on choice by user with group dcc dropdown component
    statcast_ba = statcast_player[[groupon,'Hit', 'At_Bats', 'Walk']].groupby([groupon]).sum()
    pd.options.display.float_format = '{:.3f}'.format
    statcast_ba['BA'] = statcast_ba['Hit']/statcast_ba['At_Bats']
    statcast_ba['Batting Average'] = statcast_ba['BA'] .map('{:.3f}'.format)
    
    statcast_ba = statcast_ba.reset_index()
    
    
    
    #home runs grouped on choice by user with group dcc dropdown component
    statcast_hr = statcast_player[statcast_player['events'] == 'home_run']
    statcast_hr = statcast_hr.rename(columns={'Hit': 'HR'})

    statcast_hr_count = statcast_hr[[groupon,'HR']].groupby([groupon]).sum()
    statcast_hr_count = statcast_hr_count.reset_index()
    
    #setting values/labels in bar chart viz to be dynamic based on statistic and grouping
    #                                                                  chosen by the user
    if statistic == 'Batting Average':
        df = statcast_ba
        x_val = groupon
        y_val = 'BA'
        hover_val = {'BA':False,
                     'Batting Average': True,
                    'At_Bats': True}
        title_val = 'Batting Average by ' + groupon
        y_label = 'Batting Average'

    else:
        df = statcast_hr_count
        x_val = groupon
        y_val = 'HR'
        hover_val = [y_val]
        title_val = 'Home Runs by ' + groupon
        y_label = 'Home Runs'
        
    #game log grid
    statcast_grid = statcast_player[['game_pk', 'game_date', 'Hit', 'At_Bats', 'Walk']].groupby(['game_pk', 'game_date']).sum()
    statcast_grid = statcast_grid.reset_index()
    statcast_grid.drop('game_pk', axis=1, inplace=True)
    statcast_grid = statcast_grid.sort_values(by=['game_date'], ascending=False)
    statcast_grid = statcast_grid.rename(columns={'game_date': 'Game_Date',
                                                  'Hit': 'Hits',
                                                  'At_Bats': 'ABs',
                                                  'Walk': 'Walks'})
    
    fig_grid = go.Figure(data=[go.Table(header=dict(values=list(statcast_grid.columns),
                fill_color='black',
                align='left',
                font={'size': 8,
                      'family': 'Arial Black'}),
                columnwidth = [65, 65, 65, 65],
                cells=dict(values=[statcast_grid.Game_Date, 
                                   statcast_grid.Hits, 
                                   statcast_grid.ABs,
                                   statcast_grid.Walks],
                fill_color='#323232',
                align='left',
                height=30,
                font={'size': 9}
               ))])
    
    #fig which is grouped by choice of dashboard user
    
    fig = px.bar(df, x=x_val, y=y_val, text = y_val,
                 title=title_val, labels={'x': groupon, 'y': y_label},
                color=y_val, color_continuous_scale=['orange', 'yellow', 'green'],
                hover_name=groupon, hover_data=hover_val)
    if statistic == 'Batting Average':
        fig.update_traces(texttemplate = '%{text:.3f}', textposition='inside', 
                          insidetextanchor='end', name=y_label)
    
    fig.add_scatter(x=df[x_val], y=df[y_val], mode='lines', name=y_label, 
                    marker=dict(color='white'), showlegend=False)
    
    fig.layout.plot_bgcolor = '#323232'
    fig.layout.paper_bgcolor = '#323232'
    fig.layout.font = {'color': '#FFFFFF', 'size': 8}
    fig.update_layout(margin=dict(l=50, r=50, t=50, b=50))
    
    pitch_scatter.layout.plot_bgcolor = '#323232'
    pitch_scatter.layout.paper_bgcolor = '#323232'
    pitch_scatter.layout.font = {'color': '#FFFFFF', 'size': 8}
    pitch_scatter.update_xaxes(showgrid=False, zeroline=False, range=[-1.25, 1.25])
    pitch_scatter.update_yaxes(showgrid=False, zeroline=False, range=[.75, 4.25])
    #pitch_scatter.update_layout(title='Strike Zone Scatter')
    pitch_scatter.update_layout(margin=dict(l=30, r=50, t=5, b=0))
    
    
    
    fig_grid.layout.plot_bgcolor = '#323232'
    fig_grid.layout.paper_bgcolor = '#323232'
    fig_grid.layout.font = {'color': '#FFFFFF'}
    fig_grid.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    
    return ba_card, runs_card, hr_card, rbi_card, ops_card, fig, team, fig_grid, pitch_scatter

if __name__ == '__main__':
    app.run_server()


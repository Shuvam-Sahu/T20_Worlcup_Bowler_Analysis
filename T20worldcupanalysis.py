# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

data = pd.read_excel('/content/FullT20wc2024.xlsx')

data.head()

data.shape

# Initialize the bowler DataFrame with the specified columns
bowler_columns = {'ID':[],
                   'Player':[],
                   'Innings':[],
                   'Balls':[],
                   'Overs':[],
                   'Maidens':[],
                   'Dots' :[],
                   'Runs':[],
                   'Wickets':[],
                   'Average':[],
                   'Economy':[],
                   'Strike Rate':[],
                   'Fifer':[],
                   'BBI':[],
                   }

bowler = pd.DataFrame(bowler_columns)

# Populate the 'ID' and 'Player' columns in the bowler DataFrame.

unique_bowler = data['bowler'].unique()
bowler['ID'] = range(1, len(unique_bowler) + 1)
bowler['Player'] = unique_bowler

# Calculate the number of innings played by each player.

innings_bowler = data.groupby('bowler')['match_id'].nunique().reset_index()
innings_bowler.columns = ['Player', 'Innings']
innings_bowler_dict = innings_bowler.set_index('Player')['Innings'].to_dict()
bowler['Innings'] = bowler['Player'].map(innings_bowler_dict).fillna(0)

# Calculate the total balls faced by each player, excluding wides and no-balls.

balls_bowler = data.groupby('bowler')['ball_number'].count().reset_index()
balls_bowler.columns = ['Player', 'Balls']
wides_bowler = data[data['wides'] > 0].groupby('bowler')['wides'].count().reset_index()
wides_bowler.columns = ['Player', 'Wides']
noballs_bowler = data[data['noballs'] > 0].groupby('bowler')['noballs'].count().reset_index()
noballs_bowler.columns = ['Player', 'Noballs']
balls_bowler_data = balls_bowler.merge(wides_bowler, on='Player', how='left').merge(noballs_bowler, on='Player', how='left')
balls_bowler_data = balls_bowler_data.fillna(0)
balls_bowler_data['ActualBalls'] = balls_bowler_data['Balls'] - balls_bowler_data['Wides'] - balls_bowler_data['Noballs']
balls_bowler_dict = balls_bowler_data.set_index('Player')['ActualBalls'].to_dict()
bowler['Balls'] = bowler['Player'].map(balls_bowler_dict).fillna(0)
bowler['Balls'] = bowler['Balls'].astype(int)

# Calculate the overs bowled by each player.

bowler['Overs'] = (bowler['Balls'] // 6).astype(str) + '.' + (bowler['Balls'] % 6).astype(str)

# Calculate the total runs conceded by each player.

runs_bowler = data.groupby('bowler')['runs_off_bat'].sum().reset_index()
runs_bowler.columns = ['Player', 'Runs']
wides_runs = data[data['wides'] > 0].groupby('bowler')['wides'].sum().reset_index()
wides_runs.columns = ['Player', 'Wides']
noballs_runs = data[data['noballs'] > 0].groupby('bowler')['noballs'].sum().reset_index()
noballs_runs.columns = ['Player', 'Noballs']
runs_bowler_data = runs_bowler.merge(wides_runs, on='Player', how='left').merge(noballs_runs, on='Player', how='left')
runs_bowler_data = runs_bowler_data.fillna(0)
runs_bowler_data ['ActualRuns'] = runs_bowler_data['Runs'] + runs_bowler_data['Wides'] + runs_bowler_data['Noballs']
runs_bowler_dict = runs_bowler_data.set_index('Player')['ActualRuns'].to_dict()
bowler['Runs'] = bowler['Player'].map(runs_bowler_dict).fillna(0)
bowler['Runs'] = bowler['Runs'].astype(int)

# Calculate the Wickets taken by each player.
valid_wickets_data = data[data['dismissal_type'].isin([1, 2, 3, 5])]
wickets_count = valid_wickets_data.groupby('bowler')['dismissal_type'].count().reset_index()
wickets_count.columns = ['Player', 'Wickets']
wickets_dict = wickets_count.set_index('Player')['Wickets'].to_dict()
bowler['Wickets'] = bowler['Player'].map(wickets_dict).fillna(0)
bowler['Wickets'] = bowler['Wickets'].astype(int)

# Calculate the Bowling Average for each player.

bowler['Average'] = (bowler['Runs'] / bowler['Wickets']).round(2)
bowler['Average'] = bowler['Average'].replace(np.inf, 0)

#Calculate the Bowling Economy for each player.

bowler['Economy'] = (bowler['Runs'] / ((bowler['Balls']) / 6)).round(2)

#Calculate the Bowling Strike-Rate for each player.

bowler['Strike Rate'] = (bowler['Balls'] / bowler['Wickets']).round(2)
bowler['Strike Rate'] = bowler['Strike Rate'].replace(np.inf, 0)


#Calculate the Fifer for each player.

fifer_counts = data.groupby(['match_id', 'bowler'])['dismissal_type'].count().reset_index()
fifer_counts.columns = ['MatchID', 'Player', 'Wickets']
fifer_counts = fifer_counts[fifer_counts['Wickets'] >= 5].groupby('Player')['MatchID'].count().reset_index()
fifer_counts.columns = ['Player', 'Fifer']
fifer_dict = fifer_counts.set_index('Player')['Fifer'].to_dict()
bowler['Fifer'] = bowler['Player'].map(fifer_dict).fillna(0)
bowler['Fifer'] = bowler['Fifer'].astype(int)

#Calculate the Best Figure for each player.

best_figures = data.groupby(['match_id', 'bowler']).agg({'dismissal_type': 'count', 'runs_off_bat': 'sum', 'wides': 'sum', 'noballs': 'sum'}).reset_index()
best_figures.columns = ['MatchID', 'Player', 'Wickets', 'Runs', 'Wides', 'Noballs']
best_figures['ActualRuns'] = best_figures['Runs'] + best_figures['Wides'] + best_figures['Noballs']

max_wickets = best_figures.loc[best_figures.groupby('Player')['Wickets'].idxmax()]

max_wickets['BBI'] = max_wickets['Wickets'].astype(str) + '/' + max_wickets['ActualRuns'].astype(str)
bbi_dict = max_wickets.set_index('Player')['BBI'].to_dict()
bowler['BBI'] = bowler['Player'].map(bbi_dict).fillna(0)

#Calculate Maiden overs for each players.

maiden_overs = data.groupby(['match_id', 'bowler', 'over_number']).agg({'runs_off_bat': 'sum', 'wides': 'sum', 'noballs': 'sum'}).reset_index()
maiden_overs.columns = ['MatchID', 'Player', 'Overnumber', 'Runs', 'Wides', 'Noballs']
maiden_overs['ActualRuns'] = maiden_overs['Runs'] + maiden_overs['Wides'] + maiden_overs['Noballs']
maiden_overs_counts = maiden_overs[maiden_overs['ActualRuns'] == 0].groupby('Player')['MatchID'].count().reset_index()
maiden_overs_counts.columns = ['Player', 'Maiden Overs']
maiden_overs_dict = maiden_overs_counts.set_index('Player')['Maiden Overs'].to_dict()
bowler['Maidens'] = bowler['Player'].map(maiden_overs_dict).fillna(0)
bowler['Maidens'] = bowler['Maidens'].astype(int)

# Calculate the Dot Balls by each player

dots_bowler = data[data['total_runs'] == 0].groupby('bowler')['total_runs'].count().reset_index()
dots_bowler.columns = ['Player', 'Dot Balls']
byes_bowler = data[data['byes'] > 0].groupby('bowler')['byes'].count().reset_index()
byes_bowler.columns = ['Player', 'Byes']
leg_byes_bowler = data[data['legbyes'] > 0].groupby('bowler')['legbyes'].count().reset_index()
leg_byes_bowler.columns = ['Player', 'Leg Byes']
dots_bowler_data = dots_bowler.merge(byes_bowler, on='Player', how='left').merge(leg_byes_bowler, on='Player', how='left')
dots_bowler_data = dots_bowler_data.fillna(0)
dots_bowler_data['ActualDots'] = dots_bowler_data['Dot Balls'] + dots_bowler_data['Byes'] + dots_bowler_data['Leg Byes']
dots_bowler_dict = dots_bowler_data.set_index('Player')['ActualDots'].to_dict()
bowler['Dots'] = bowler['Player'].map(dots_bowler_dict).fillna(0)
bowler['Dots'] = bowler['Dots'].astype(int)

# Calculate the Dot Balls percentage by each player

dots_bowler_pct = (bowler['Dots'] / bowler['Balls']) * 100
bowler['Dot Ball %'] = dots_bowler_pct.round(2)

# Calculate the Dot Balls rate by each player

dot_rate_bowler = (bowler['Balls'] / bowler['Dots'])
bowler['Dot Rate'] = dot_rate_bowler.round(2)
bowler['Dot Rate'] = bowler['Dot Rate'].replace(np.inf, 0)

# Calculate the 4s conceded by each player

fours_bowler = data[data['runs_off_bat'] == 4].groupby('bowler')['runs_off_bat'].count().reset_index()
fours_bowler.columns = ['Player', 'fours']
fours_bowler_dict = fours_bowler.set_index('Player')['fours'].to_dict()
bowler['4s'] = bowler['Player'].map(fours_bowler_dict).fillna(0)
bowler['4s'] = bowler['4s'].astype(int)

# Calculate the 6s conceded by each player

sixes_bowler = data[data['runs_off_bat'] == 6].groupby('bowler')['runs_off_bat'].count().reset_index()
sixes_bowler.columns = ['Player', 'sixes']
sixes_bowler_dict = sixes_bowler.set_index('Player')['sixes'].to_dict()
bowler['6s'] = bowler['Player'].map(sixes_bowler_dict).fillna(0)
bowler['6s'] = bowler['6s'].astype(int)

# Calculate runs conceded by bowlers in boundaries.
bowler['Boundary Runs'] = ((bowler['4s'] * 4) + (bowler['6s'] * 6))
bowler['Boundary Runs'] = bowler['Boundary Runs'].astype(int)

# Calculate the Boundary % conceded by bowlers in boundaries.
bowler['Boundary %'] = (((bowler['4s'] * 4) + (bowler['6s'] * 6)) / bowler['Runs']) * 100
bowler['Boundary %'] = bowler['Boundary %'].round(2)

# Calculate the Strike Rotation and Strike Rotation pct conceded by bowlers.

strike_rotation_bowler = data[(data['runs_off_bat'] > 0) & (data['runs_off_bat'] < 4) ].groupby('bowler')['runs_off_bat'].count().reset_index()
strike_rotation_bowler.columns = ['Player', 'Strike Rotation']
strike_rotation_bowler_dict = strike_rotation_bowler.set_index('Player')['Strike Rotation'].to_dict()
bowler['Strike Rotation'] = bowler['Player'].map(strike_rotation_bowler_dict).fillna(0)
bowler['Strike Rotation'] = bowler['Strike Rotation'].astype(int)

strike_rotation_pct_bowler = (bowler['Strike Rotation'] / bowler['Runs']) * 100
bowler['Strike Rotation %'] = strike_rotation_pct_bowler.round(2)

bowler.head(250)

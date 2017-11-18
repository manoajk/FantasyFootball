import pandas as pd
import numpy as np

# '../data_files/'

regular_season_games = 13
total_teams = 12
playoff_teams = 6

non_playoff = total_teams - playoff_teams

# teams = {}
# with open("standings.txt") as standings_file:
#     rank = 1

#     for line in standings_file:
#         splitter = line.replace("\n", "").split("\t")
#         if not splitter[0].__contains__('TEAM') and len(splitter) > 1:
#             team_and_owners = splitter[0].split('(')
#             points_for = float(splitter[1])
#             points_against = float(splitter[2])
#             record = splitter[5]
#             record_list = [int(num) for num in record.split('-')]
#             streak = splitter[6]

#             team = team_and_owners[0]
#             owners = team_and_owners[1].replace(')', "")

#             win = record_list[0]
#             losses = record_list[1]
#             ties = record_list[2]
#             games_played = win + losses + ties
#             pct = (win + 0.5 * ties) / games_played
# #             max_win = win + (regular_season_games - games_played)

#             team_info = {}
#             team_info['Rank'] = rank
#             team_info['Team Name'] = team
#             team_info['Owners'] = owners
#             team_info['Points For'] = points_for
#             team_info['Points Against'] = points_against
#             team_info['Record'] = record
#             team_info['Wins'] = win
#             team_info['Games Played'] = games_played
#             team_info['Pct (%)'] = pct
# #             team_info['Max Wins'] = max_win

#             # print(max_wins)
# #             if win in wins:
# #                 wins[win] += 1
# #             else:
# #                 wins[win] = 1

# #             if max_win in max_wins:
# #                 max_wins[max_win] += 1
# #             else:
# #                 max_wins[max_win] = 1

#             teams[rank] = team_info
#             rank += 1

# df = pd.DataFrame.from_dict(teams).transpose()
# # print("Wins Filter", np.sum(df['Max Wins'] > 7))
# # print("Games Played", df.get('Games Played'))
# # print("ONe row", df.loc[[2]])
# # for index, row in df.iterrows():
# #     print(row['Team Name'])
# # games_left = regular_season_games - df['Games Played']
# # df['Clinched'] = df['Wins'] > (df.iloc[playoff_teams]['Wins'] + games_left)
# # df['Eliminated'] = (df['Wins'] + games_left) < df.iloc[playoff_teams - 1]['Wins']

columns=['Rank', 'Team Name', 'Owners', 'Points For',
         'Points Against', 'Record', 'Wins', 'Games Played', 'Pct (%)']
df = pd.DataFrame(columns=columns)

with open("../data_files/standings.txt") as s_file:
    rank = 1

    for line in s_file:
        splitter = line.replace("\n", "").split("\t")
        if not splitter[0].__contains__('TEAM') and len(splitter) > 1:
            team_and_owners = splitter[0].split('(')
            points_for = float(splitter[1])
            points_against = float(splitter[2])
            record = splitter[5]
            record_list = [int(num) for num in record.split('-')]
            streak = splitter[6]

            team = team_and_owners[0]
            owners = team_and_owners[1].replace(')', "")

            win = record_list[0]
            losses = record_list[1]
            ties = record_list[2]
            games_played = win + losses + ties
            pct = (win + 0.5 * ties) / games_played
            
            df.loc[rank] = [rank, team, owners, points_for, points_against, record, win, games_played, pct]
            rank += 1

df.Rank = df.Rank.astype(int)

games_left = regular_season_games - df['Games Played']
df['Wins for Clinching'] = (df.iloc[playoff_teams]['Wins'] + games_left) - df['Wins'] + 1
df['Losses for Elimination'] = (df['Wins'] + games_left) - df.iloc[playoff_teams - 1]['Wins']

to_clinch = df[df['Wins for Clinching'] == 1]

fringe = df[df["Wins"] == df.iloc[playoff_teams]['Wins']]

outside_length = len(fringe)

fringe_teams = fringe["Rank"].max() - fringe["Rank"].min() + 1

# if outside_length == fringe_teams:
#     criteria = "ALL"
# else:
#     criteria = "Choose " + str(outside_length) + " out of " + str(fringe_teams)
criteria = "ALL" if outside_length == fringe_teams else "Choose " + str(outside_length) + " out of " + str(fringe_teams)

losses_for_clinch = [criteria + " of the following need to occur:"]
for index, row in fringe.iterrows():
    losses_for_clinch.append(" - " + row['Team Name'] + " (" + row["Record"] + ") Loss")
# losses_for_clinch = "\n".join(losses_for_clinch)
# print(losses_for_clinch)

output = []
output.append("Without further ado,\n" \
            + "PLAYOFF PICTURE brought to you by a Julin’ Around Manjie\n" \
            + "[*] Clinched Homefield Advantage in the Playoffs\n" \
            + "[z] Clinched First-Round Bye\n" \
            + "[x] Clinched Playoff Berth\n" \
            + "[e] Eliminated From Playoff Contention\n\n")
for index, row in df.iterrows():
    if row['Wins for Clinching'] == 0:
        output.append("[x]")
	# potentially put this in dataframe itself?
	# for symbol_string in clinch_symbols:
	# 	if row[symbol_string] <= 0:
	# 		output.append(clinch_symbols[symbol_string])
    # if row['Wins to Clinch Playoffs'] == 0:
    #     output.append("[x]")
    output.append("\t" + str(row['Rank']) + ") [" + row['Record'] + "] "+ row['Team Name'] + " (" + row['Owners'] + ")")
    and_or = None
    if row['Wins for Clinching'] == 1:
        and_or = "OR"
    elif row['Wins for Clinching'] == 2:
        and_or = "AND"
    if and_or != None:
#         space = " "*3
        output.append("\n\t\tClinching Scenarios -\n\t   a) Win\n\t\t")
        output.append(and_or)
        output.append("\n\t   b) ")
        output.append("\n\t\t".join(losses_for_clinch))
    output.append("\n\n")
output = "".join(output)
print(output)

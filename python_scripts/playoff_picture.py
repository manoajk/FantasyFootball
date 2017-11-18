import pandas as pd
import numpy as np

regular_season_games = 13
total_teams = 12
playoff_teams = 6
playoff_bye_teams = 8 - playoff_teams

standings_file = 'standings.txt'

non_playoff = total_teams - playoff_teams

symbols = {}
playoff_clinch_string = "Wins to Clinch Playoffs"
symbols[playoff_clinch_string] = "x"

bye_clinch_string = "Wins to Clinch First-Round Bye"
symbols[bye_clinch_string] = "z"

homefield_clinch_string = "Wins to Clinch Homefield Advantage"
symbols[homefield_clinch_string] = "*"

elim_string = 'Losses till Playoff-Ineligbile'
symbols[elim_string] = "e"


def parse_standings():
    columns=['Rank', 'Team Name', 'Owners', 'Points For',
         'Points Against', 'Record', 'Wins', 'Games Played', 'Pct (%)']
    dataframe = pd.DataFrame(columns=columns)

    with open('../data_files/' + standings_file) as s_file:
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

                dataframe.loc[rank] = [rank, team, owners, points_for, points_against, record, win, games_played, pct]
                rank += 1

    return dataframe

def team_loss_string(row):
    output = row['Team Name']
    output += " ("
    output += row["Record"]
    output += ") Loss"
    return output
    
def string_for_team_losses(filtered_df):
    output = []

    length = len(filtered_df)
    rnge = filtered_df["Rank"].max() - filtered_df["Rank"].min() + 1

    if (length == 0): return output
    if (length == 1): return [team_loss_string(filtered_df.iloc[0])]
    keyword = length
    if length == rnge:
        keyword = 'BOTH' if length == 2 else 'ALL'
    output += [keyword + " of the following need(s) to occur:"]
    for index, row in filtered_df.iterrows():
        output += [" - " + team_loss_string(row)]

    return output



def keep_teams_below(df, safezone_num, column_string):
    # if df == None or safezone_num < 1 or safezone_num > len(df) or column_string == None or column_string not in df: return ''

    games_left = regular_season_games - df['Games Played']
    df[column_string] = (df.iloc[safezone_num]['Wins'] + games_left) - df['Wins'] + 1

    fringe = df[df["Wins"] == df.iloc[safezone_num]['Wins']]
    outside_length = len(fringe)
    fringe_teams = fringe["Rank"].max() - fringe["Rank"].min() + 1

    return string_for_team_losses(fringe)

def catchup_to_teams_above(df, safezone_num, column_string):
    # if df == None or safezone_num < 1 or safezone_num > len(df) or column_string == None or column_string not in df: return ''

    games_left = regular_season_games - df['Games Played']
    df[column_string] = (df['Wins'] + games_left) - df.iloc[safezone_num - 1]['Wins'] + 1
    
    barely_in = df[df["Wins"] == df.iloc[safezone_num - 1]['Wins']]
    barely_in_length = len(barely_in)
    barely_in_teams = barely_in["Rank"].max() - barely_in["Rank"].min() + 1

    return string_for_team_losses(barely_in)

def set_status(df, symbols):
    # if df != None and symbols != None:
    if True:
        df['Status'] = ''
        for key in symbols:
            if key in df.columns:
                df.loc[df[key] == 0, 'Status'] += symbols[key]
        df.loc[df['Status'] != '', 'Status'] = '[' + df['Status'] + ']'


def new_tab_lines(num_tabs=0, num_lines=1):
    return num_lines * '\n' + num_tabs * '\t'


df = parse_standings()

playoff_clinch_other_teams = keep_teams_below(df, playoff_teams, playoff_clinch_string)
bye_clinch_other_teams = keep_teams_below(df, playoff_bye_teams, bye_clinch_string)
homefield_clinch_other_teams = keep_teams_below(df, 1, homefield_clinch_string)

non_elimination = catchup_to_teams_above(df, playoff_teams, elim_string)

set_status(df, symbols)


def criteria_builder(criteria_string, display_title, string_arr):
    # print("STRING ARR", string_arr)
    output = []
    and_or = None
    if row[criteria_string] == 1:
        and_or = "OR"
    elif row[criteria_string] == 2:
        and_or = "AND"
    if and_or != None:
#         space = " "*3
        two_tabs = new_tab_lines(2)
        one_tab = new_tab_lines(1)
        # output.append(two_tabs)
        # output.append(display_title)
        # output.append(one_tab)
        # output.append("   a) Win")
        # output.append(two_tabs)
        # output.append(and_or)
        # output.append(one_tab)
        # output.append("   b) ")
        # output.append(two_tabs.join(string_arr))

        output += two_tabs
        output += display_title
        output += " -"
        # output += "Clinching Scenarios -"
        output += one_tab
        output += "   a) Win"
        output += two_tabs
        output += and_or
        output += one_tab
        output += "   b) "
        print("STRING ARR", string_arr)
        output += two_tabs.join(string_arr)

    return output



output = []
output.append("Without further ado,\n" \
            + "PLAYOFF PICTURE brought to you by a Julin’ Around Manjie\n" \
            + "[*] Clinched Homefield Advantage in the Playoffs\n" \
            + "[z] Clinched First-Round Bye\n" \
            + "[x] Clinched Playoff Berth\n" \
            + "[e] Eliminated From Playoff Contention\n\n")
for index, row in df.iterrows():

    output += row['Status']
    output += "\t"
    output += str(int(row['Rank']))
    output +=  ") ["
    output += row['Record']
    output += "] "
    output += row['Team Name']
    output += " ("
    output += row['Owners']
    output += ")"

    output += criteria_builder(playoff_clinch_string, 'Clinching Scenarios', playoff_clinch_other_teams)
    output += criteria_builder(elim_string, 'Preventing Elimination', non_elimination)
#   and_or = None
#   if row['Wins to Clinch Playoffs'] == 1:
#       and_or = "OR"
#   elif row['Wins to Clinch Playoffs'] == 2:
#       and_or = "AND"
#   if and_or != None:
# #         space = " "*3
#       two_tabs = new_tab_lines(2)
#       one_tab = new_tab_lines(1)

#       output += two_tabs
#       output += "Clinching Scenarios -"
#       output += one_tab
#       output += "   a) Win"
#       output += two_tabs
#       output += and_or
#       output += one_tab
#       output += "   b) "
#       output += two_tabs.join(playoff_clinch_other_teams)

    output += "\n\n"
output = "".join(output)
print(output)

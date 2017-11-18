import pandas as pd
import numpy as np

def parse_standings(standings_file, path_to_data):
    columns=['Rank', 'Team Name', 'Owners', 'Points For',
         'Points Against', 'Record', 'Wins', 'Games Played', 'Pct (%)']
    dataframe = pd.DataFrame(columns=columns)

    with open(path_to_data + standings_file) as s_file:
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
    if type(df) == None or safezone_num < 1 or safezone_num > len(df) or type(column_string) == None:# or column_string not in df.columns:
            return ''
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
    scenarios = []
    df['Status'] = ''

    for key in symbols:
        if symbols[key][1]: scenarios.append((key, symbols[key][3], keep_teams_below(df, symbols[key][2], key), True))
        else: scenarios.append((key, symbols[key][3], catchup_to_teams_above(df, symbols[key][2], key), False))

        if key in df.columns: df.loc[df[key] <= 0, 'Status'] += symbols[key][0]
    df.loc[df['Status'] != '', 'Status'] = '[' + df['Status'] + ']'

    return scenarios

def new_tab_lines(num_tabs=0, num_lines=1):
    return num_lines * '\n' + num_tabs * '\t'

def criteria_builder(and_or, display_title, string_arr):
    output = []
    if and_or != None:
        two_tabs = new_tab_lines(2)
        one_tab = new_tab_lines(1)

        output += two_tabs
        output += display_title
        output += " -"
        output += one_tab
        output += "   a) Win"
        output += two_tabs
        output += and_or
        output += one_tab
        output += "   b) "
        output += two_tabs.join(string_arr)
        output += "\n"

    return output

def keep_below_criteria_builder(row, criteria_string, display_title, string_arr):
    and_or = None
    if row[criteria_string] == 1: and_or = "OR"
    elif row[criteria_string] == 2: and_or = "AND"
    return criteria_builder(and_or, display_title, string_arr)
        
def catchup_above_criteria_builder(row, criteria_string, display_title, string_arr):
    and_or = None
    if row[criteria_string] == 2: and_or = "OR"
    elif row[criteria_string] == 1: and_or = "AND"
    return criteria_builder(and_or, display_title, string_arr)

def base_symbols(playoff_teams, playoff_bye_teams):
    clinch_symbols = {}

    clinch_symbols['Wins to Clinch Homefield Advantage'] = ["*", True, 1, "Homefield Advantage Clinching Scenarios"]
    clinch_symbols['Wins to Clinch First-Round Bye'] = ["z", True, playoff_bye_teams, "Bye-Week Clinching Scenarios"]
    clinch_symbols['Wins to Clinch Playoffs'] = ["x", True, playoff_teams, "Playoff Clinching Scenarios"]
    clinch_symbols['Losses till Playoff-Ineligbile'] = ["e", False, playoff_teams, "Playoff Elimination Prevention Scenarios"]

    return clinch_symbols

def main(standings_file, path_to_data, regular_season_games, total_teams, playoff_teams, playoff_bye_teams, symbols):
    df = parse_standings(standings_file, path_to_data)
    non_playoff = total_teams - playoff_teams
    scenarios = set_status(df, symbols)

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
        for scenario in scenarios:
            if scenario[-1]: output += keep_below_criteria_builder(row, scenario[0], scenario[1], scenario[2])
            else: output += catchup_above_criteria_builder(row, scenario[0], scenario[1], scenario[2])
        output += "\n\n"
    return "".join(output), df

######################################

usePJC = True

regular_season_games = 13
total_teams = 12
path_to_data = '../data_files/'
if usePJC:
    playoff_teams = 6
    s_file = 'pjc_standings_11.txt'
else:
    playoff_teams = 8
    s_file = 'gt_standings_11.txt'

playoff_bye_teams = 8 - playoff_teams

symbols = base_symbols(playoff_teams, playoff_bye_teams)
print_output, dataframe = main(s_file, path_to_data, regular_season_games, total_teams, playoff_teams, playoff_bye_teams, symbols)

print(print_output)
# print(dataframe)
import pandas as pd
import numpy as np

#### Column Names ###
RANK = 'Rank'
TEAM = 'Team Name'
OWNERS = 'Owners'
PF = 'Points For'
PA = 'Points Against'
RECORD = 'Record'
WINS = 'Wins'
GP = 'Games Played'
PCT = 'Pct (%)'
STATUS = 'Status'
#####################

def num_to_word(num):
    num_word_dict = {1: "One", 2: "Two", 3: "Three",
                     4: "Four", 5: "Five", 6: "Six",
                     7: "Seven", 8: "Eight", 9: "Nine",
                     10: "Ten", 11: "Eleven", 12: "Twelve",
                     13: "Thirteen"}
    if type(num) is float: num = int(num)
    if type(num) is int: return num_word_dict[num].upper()
    return num

def parse_standings(standings_file, path_to_data, columns):
    """ Specific .txt parser given ESPN Fantasy Format """
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
    """ Simple representation of team that is required to lose in scenario """
    return row['Team Name'] + " (" + row['Record'] + ") Loss"
    
def string_for_team_losses(filtered_df, threshold, push_teams_below):
    """ Combines the scenarios needed for the external losses """
    output = []
    rnge = filtered_df[RANK].max() - filtered_df[RANK].min() + 1
    if push_teams_below:
        if len(filtered_df[filtered_df[RANK] > threshold]) == 0: return []
        length = filtered_df[RANK].max() - threshold
    else:
        length = len(filtered_df[filtered_df[RANK] >= threshold])

    if (len(filtered_df) <= 0 or length <= 0): return output
    if (rnge == 1): return [team_loss_string(filtered_df.iloc[0])]
    keyword = int(length)
    if length == rnge:
        keyword = 'BOTH' if length == 2 else 'ALL'
    output += [str(num_to_word(keyword)) + " of the following need(s) to occur:"]
    for index, row in filtered_df.iterrows():
        output += [" - " + team_loss_string(row)]

    return output


def keep_teams_below(df, safezone_num, column_string):
    """ Finds the combination of teams needed to push below the safezone """
    if type(df) == None or safezone_num < 1 or safezone_num > len(df) or type(column_string) == None: return ''

    games_left = regular_season_games - df[GP]
    df[column_string] = (df.iloc[safezone_num][WINS] + games_left) - df[WINS] + 1

    fringe = df[df[WINS] == df.iloc[safezone_num][WINS]]

    return string_for_team_losses(fringe, safezone_num, True)

def catchup_to_teams_above(df, catchup_num, column_string):
    """ Finds the combination of teams needed to falter to reach the catchup position """
    if type(df) == None or catchup_num < 1 or catchup_num > len(df) or type(column_string) == None: return ''
    games_left = regular_season_games - df[GP]
    df[column_string] = (df[WINS] + games_left) - df.iloc[catchup_num - 1][WINS] + 1
    
    barely_in = df[df[WINS] == df.iloc[catchup_num - 1][WINS]]

    return string_for_team_losses(barely_in, catchup_num, False)

def set_status(df, symbols):
    """ Sets statuses for teams based on the symbol-keys """
    scenarios = []
    df[STATUS] = ''

    for key in symbols:
        if symbols[key][2] > 0:
            if symbols[key][1]:
                func = keep_teams_below
                keep_below = True
            else:
                func = catchup_to_teams_above
                keep_below = False
            scenarios.append((key, symbols[key][3], func(df, symbols[key][2], key), keep_below))

        if key in df.columns: df.loc[df[key] <= 0, 'Status'] += symbols[key][0]
    df.loc[df[STATUS] != '', STATUS] = '[' + df[STATUS] + ']'

    return scenarios

def new_tab_lines(num_tabs=0, num_lines=1):
    """ Dynamic spacing for writing """
    return num_lines * '\n' + num_tabs * '\t'

# def criteria_builder(and_or, display_title, string_arr, keep_below_bool):
def criteria_builder(row, criteria_string, display_title, string_arr, keep_below_bool):
    """ Takes care of combining the criteria together """
    and_or = None
    check_col = row[criteria_string]
    output = []

    if keep_below_bool:
        if check_col == 1: and_or = "OR"
        elif check_col == 2: and_or = "AND"
    else:
        if check_col == 2: and_or = "OR"
        elif check_col == 1: and_or = "AND"

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

def base_symbols(playoff_teams, playoff_bye_teams):
    clinch_symbols = {}

    clinch_symbols['Wins to Clinch Homefield Advantage'] = ["*", True, 1, "Homefield Advantage Clinching Scenarios"]

    if playoff_bye_teams != 0:
        clinch_symbols['Wins to Clinch First-Round Bye'] = ["z", True, playoff_bye_teams, "Bye-Week Clinching Scenarios"]

    clinch_symbols['Wins to Clinch Playoffs'] = ["x", True, playoff_teams, "Playoff Clinching Scenarios"]

    if playoff_bye_teams != 0:
        clinch_symbols['Wins to Prevent Consolation Bracket'] = ["s", True, playoff_teams + playoff_bye_teams, "Playoff Clinching Scenarios"]

    clinch_symbols['Losses till Consolation Bracket'] = ["e", False, playoff_teams, "Consolation Bracket Prevention Scenarios"]

    return clinch_symbols

def base_message():
    return "Without further ado,\n" \
            + "PLAYOFF PICTURE brought to you by a Julin’ Around Manjie\n" \
            + "[*] Clinched Homefield Advantage in the Playoffs\n" \
            + "[z] Clinched First-Round Bye\n" \
            + "[x] Clinched Playoff Berth\n" \
            + "[s] Safe from Consolation\n" \
            + "[e] Clinched Punishment Contention\n\n"

def print_team(row,):
    return row[STATUS] + "\t" + str(int(row[RANK])) + ") [" + row[RECORD] + "] " + row[TEAM] + " (" + row[OWNERS] + ")"

def main(standings_file, path_to_data, regular_season_games, total_teams, playoff_teams, playoff_bye_teams, symbols):
    columns=[RANK, TEAM, OWNERS, PF, PA, RECORD, WINS, GP, PCT]
    df = parse_standings(standings_file, path_to_data, columns)
    non_playoff = total_teams - playoff_teams
    scenarios = set_status(df, symbols)

    output = []
    output += base_message()
    for index, row in df.iterrows():
        output += print_team(row)
        for scenario in scenarios:
            output += criteria_builder(row, scenario[0], scenario[1], scenario[2], scenario[3])
        output += "\n\n"
    return "".join(output), df

######################################

usePJC = False

regular_season_games = 13
total_teams = 12
path_to_data = '../data_files/'
current_week = 12
symbols = {}

if usePJC:
    playoff_teams = 6
    standings_file = 'pjc'

else:
    playoff_teams = 8
    standings_file = 'gt'

standings_file += '_standings_' + str(current_week) + '.txt'

playoff_bye_teams = 8 - playoff_teams

symbols = base_symbols(playoff_teams, playoff_bye_teams)
print_output, dataframe = main(standings_file, path_to_data, regular_season_games, total_teams, playoff_teams, playoff_bye_teams, symbols)

print(print_output)
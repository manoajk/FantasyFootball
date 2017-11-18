import pandas as pd
import numpy as np

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
    return row['Team Name'] + " (" + row['Record'] + ") Loss"
    
def string_for_team_losses(filtered_df, rank_col, wins_col, safezone_num, push_teams_below):
    output = []
    rnge = filtered_df[rank_col].max() - filtered_df[rank_col].min() + 1
    
#     print("SAFEZONE", safezone_num)
#     print(filtered_df)
    if push_teams_below:

#         print("BELOW", filtered_df[filtered_df[rank_col] > safezone_num])
        
        if len(filtered_df[filtered_df[rank_col] > safezone_num]) == 0: return []
#         length = filtered_df.loc[safezone_num][rank_col] - filtered_df[rank_col].min() + 1
#         length = safezone_num - filtered_df[rank_col].min() + 1
        length = filtered_df[rank_col].max() - safezone_num
#         print(filtered_df[rank_col].max(), '-', safezone_num)
#         print("LENGTH/RANGE", length, "/", rnge)
#         print("")
    else:
#         print("ABOVE", filtered_df[filtered_df[rank_col] <= safezone_num])
        if len(filtered_df[filtered_df[rank_col] <= safezone_num]) == 0: return []
#         length = filtered_df[rank_col].max() - filtered_df.loc[safezone_num][rank_col] + 1
        length = filtered_df[rank_col].max() - safezone_num + 1
#         print("LENGTH/RANGE", length, "/", rnge)
#         print("")

    if (length <= 0): return output
    if (length == 1): return [team_loss_string(filtered_df.iloc[0])]
    keyword = int(length)
    if length == rnge:
        keyword = 'BOTH' if length == 2 else 'ALL'
    output += [str(num_to_word(keyword)) + " of the following need(s) to occur:"]
    for index, row in filtered_df.iterrows():
        output += [" - " + team_loss_string(row)]

    return output


# consolidate keep_teams_below() and catchup_to_teams_above()
def keep_teams_below(df, safezone_num, column_string, gp_col, wins_col, rank_col):
    if type(df) == None or safezone_num < 1 or safezone_num > len(df) or type(column_string) == None:# or column_string not in df.columns:
            return ''
    games_left = regular_season_games - df[gp_col]
    df[column_string] = (df.iloc[safezone_num][wins_col] + games_left) - df[wins_col] + 1

    fringe = df[df[wins_col] == df.iloc[safezone_num][wins_col]]
    outside_length = len(fringe)
    fringe_teams = fringe[rank_col].max() - fringe[rank_col].min() + 1

    return string_for_team_losses(fringe, rank_col, wins_col, safezone_num, True)

def catchup_to_teams_above(df, safezone_num, column_string, gp_col, wins_col, rank_col):
    # if df == None or safezone_num < 1 or safezone_num > len(df) or column_string == None or column_string not in df: return ''

    games_left = regular_season_games - df[gp_col]
    df[column_string] = (df[wins_col] + games_left) - df.iloc[safezone_num - 1][wins_col] + 1
    
    barely_in = df[df[wins_col] == df.iloc[safezone_num - 1][wins_col]]
    barely_in_length = len(barely_in)
    barely_in_teams = barely_in[rank_col].max() - barely_in[rank_col].min() + 1

    return string_for_team_losses(barely_in, rank_col, wins_col, safezone_num, False)

def set_status(df, symbols, gp_col, wins_col, rank_col, status_col):
    scenarios = []
    df[status_col] = ''

    for key in symbols:
        if symbols[key][2] > 0:
            if symbols[key][1]: scenarios.append((key,
                                        symbols[key][3],
                                        keep_teams_below(df, symbols[key][2], key, gp_col, wins_col, rank_col),
                                        True))
            else: scenarios.append((key,
                            symbols[key][3],
                            catchup_to_teams_above(df, symbols[key][2], key, gp_col, wins_col, rank_col),
                            False))

        if key in df.columns: df.loc[df[key] <= 0, 'Status'] += symbols[key][0]
    df.loc[df[status_col] != '', status_col] = '[' + df[status_col] + ']'

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


# consolidate keep_below... and catchup_above...
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

def base_message():
    return "Without further ado,\n" \
            + "PLAYOFF PICTURE brought to you by a Julin’ Around Manjie\n" \
            + "[*] Clinched Homefield Advantage in the Playoffs\n" \
            + "[z] Clinched First-Round Bye\n" \
            + "[x] Clinched Playoff Berth\n" \
            + "[e] Eliminated From Playoff Contention\n\n"

def print_team(row, status_col, rank_col, record_col, team_col, owners_col):
    return row[status_col] + "\t" + str(int(row[rank_col])) + ") [" + row[record_col] + "] " + row[team_col] + " (" + row[owners_col] + ")"


def main(standings_file, path_to_data, regular_season_games, total_teams, playoff_teams, playoff_bye_teams, symbols):
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

    columns=[RANK, TEAM, OWNERS, PF, PA, RECORD, WINS, GP, PCT]
    df = parse_standings(standings_file, path_to_data, columns)
    non_playoff = total_teams - playoff_teams
    scenarios = set_status(df, symbols, GP, WINS, RANK, STATUS)

    output = []
    output += base_message()
    for index, row in df.iterrows():
        output += print_team(row, STATUS, RANK, RECORD, TEAM, OWNERS)
        for scenario in scenarios:
            # consolidate below
#             print(row[TEAM], "SCENARIO", scenario)
            if scenario[-1]: output += keep_below_criteria_builder(row, scenario[0], scenario[1], scenario[2])
            else: output += catchup_above_criteria_builder(row, scenario[0], scenario[1], scenario[2])
#             print("")
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
# print(playoff_teams)
# print(dataframe)
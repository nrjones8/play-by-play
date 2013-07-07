# Nick Jones

import re
import math
import os

'''
TODO: 
- players re-enter at start of new quarters
- one pass through to get every player who scored -- ignore others? Sure. 
'''

GAME_LENGTH = 48


class Game:

    def __init__(self, teams, times, scores, game_id):
        self.teams = teams
        self.times = times
        self.scores = scores
        self.game_id = game_id
        # Could add things like home/away etc.

    def get_diff(self, team_with_respect_to):
        # Get differential with respect to team <team_with_respect_to>
        other_team = self.teams[0] if team_with_respect_to == self.teams[1] else self.teams[1]
        differential = [self.scores[team_with_respect_to][i] - self.scores[other_team][i] for i in range(len(self.times))]
        return differential

def readAllGames(fileName = 'playbyplay20120510040.txt'):
    f = open(fileName, 'r')
    all_lines = f.readlines()
    f.close()

    # All lines for current game
    cur_game = []

    # {team_name -> [list of game objs]}
    team_to_games = {}

    for i in range(1, len(all_lines)):
        cur_line = all_lines[i]
        if cur_line.split('\t')[1] == '1' and i != 1:
            # New game about to start, clear the lines and process past game
            process_cur_game(cur_game, team_to_games)
            cur_game = []

        cur_game.append(all_lines[i])

    return team_to_games
    

def process_cur_game(game_lines, team_to_games):
    '''
    Given <game_lines> (the lines corresponding to given game), update
    the <team_to_games> dictionary to include the game corresponding
    to <game_lines>
    '''
    teams, times, scores, game_id = parse_timeline(game_lines)
    game = Game(teams, times, scores, game_id)
    for t in teams:
        team_to_games.setdefault(t, []).append(game)
    

def parse_timeline(all_lines):
    # Last 6 characters of first column correspond to two teams playing
    game_id = all_lines[0].split()[0]

    team_str = game_id[-6:]
    teams = (team_str[:3], team_str[3:])

    # Time series for each team
    all_times = []
    scores = dict(zip(teams, [[], []]))
    
    # Parse lines for scores, player whos scored, and when substitutions occur
    score = r'\[([A-z]{3})\s(\d*)\-(\d*)\]'
    quarter_end = r'End of\s(.*)'

    for i in range(len(all_lines)): 
        line = all_lines[i]
        split = line.split('\t')
        time_elapsed = convert_time(split[2])
        # i.e. [NYK 11-12]
        
        score_update = re.search(score, line)
        if score_update != None:
            # Update time seris
            team, first_score, second_score = score_update.groups()
            other_team = teams[0] if team == teams[1] else teams[1]

            scores[team].append(int(first_score))
            scores[other_team].append(int(second_score))
            
            all_times.append(time_elapsed)

    return teams, all_times, scores, game_id


def writeTeamTS(times, scores, teams, outFile = 'oneSeries.csv'):
    ''' Note that scores are with respect to teams[0] - teams[1] '''
    out = open(outFile, 'w')
    out.write(teams[0] + ' ' + teams[1] + '\n')
    out.write('time, diff\n')

    for t, s in zip(times, scores):
        out.write(str(t) + ', ' + str(s) + '\n')
    out.close()

def convert_time(fileTime):
    '''
    Takes a string from the file\'s TimeRemaining column,
    such as 00:45:52 and converts it to a decimal of 
    "time elapsed"
    '''
    tRexp = r'(\d{2}):(\d{2}):(\d{2})'
    hrs, mins, secs = re.search(tRexp, fileTime).groups()
    elapsed = GAME_LENGTH - (int(mins) + int(secs) / 60.0)
    return elapsed

def write_games_to_files(team = 'MIA'):
    all_games = readAllGames()
    team_games = all_games[team]
    # Set up directory for data
    make_dir_for_team(team)

    for g in team_games:
        # Could use sets here instead
        other_team = g.teams[0] if g.teams[1] == team else g.teams[1]
        file_name = team + '/' + g.game_id + '.csv'
        differential = g.get_diff(team)
        write_one_game_to_file(file_name, g.times, differential)

def make_dir_for_team(team):
    ''' Make directory to store this team's timeline data '''
    try:
        os.mkdir(team)
    except OSError:
        print "Directory '%s' already existed, nothing overwritten" % team

def write_one_game_to_file(file_name, times, diffs):
    ''' Write to <file_name> the time and point differential as a .csv'''
    try:
        f = open(file_name, 'w')
        for t, d in zip(times, diffs):
            f.write("%s, %i \n" % (t, d))
        f.close()
        print 'Wrote %s successfully!' % file_name
    except:
        print 'Failed to create file %s!' % file_name

if __name__ == "__main__":
    write_games_to_files()




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

    def __init__(self, teams, timeline, date):
        self.teams = teams
        self.timeline = timeline
        self.date = date
        # Could add things like home/away etc.

class TimeLine:

    def __init__(self, times, scores):
        self.times = times
        self.teams = scores.keys()
        self.scores = [scores[self.teams[0]], scores[self.teams[1]]]

    def get_diff(self, team_with_respect_to):
        # Get differential with respect to team <team_with_respect_to>
        index_with_respect_to = 1 if self.teams[1] == team_with_respect_to else 0
        other_index = (index_with_respect_to + 1) % 2
        differential = [self.scores[index_with_respect_to][t] - self.scores[other_index][t] for t in range(len(self.times))]
        return differential

def readAllGames(fileName = 'playbyplay20120510040.txt'):
    f = open(fileName, 'r')
    allLines = f.readlines()
    f.close()

    # All lines for current game
    cur_game = []

    # {team_name -> [list of game objs]}
    team_to_games = {}

    for i in range(1, len(allLines)):
        cur_line = allLines[i]
        if cur_line.split('\t')[1] == '1' and i != 1:
            # New game about to start, clear the lines and process past game
            process_cur_game(cur_game, team_to_games)
            cur_game = []

        cur_game.append(allLines[i])

    return team_to_games
    

def process_cur_game(game_lines, team_to_games):
    '''
    Given <game_lines> (the lines corresponding to given game), update
    the <team_to_games> dictionary to include the game corresponding
    to <game_lines>
    '''
    teams, game_timeline, date = parseTimeline(game_lines)
    game = Game(teams, game_timeline, date)
    for t in teams:
        team_to_games.setdefault(t, []).append(game)
    

def parseTimeline(allLines):
    # Last 6 characters of first column correspond to two teams playing
    game_info = allLines[0].split()[0]
    game_date = game_info[:-6]

    teamStr = game_info[-6:]
    teams = (teamStr[:3], teamStr[3:])

    # Time series for each team
    allTimes = []
    scores = dict(zip(teams, [[], []]))
    
    # Parse lines for scores, player whos scored, and when substitutions occur
    score = r'\[([A-z]{3})\s(\d*)\-(\d*)\]'
    quarterEnd = r'End of\s(.*)'

    for i in range(len(allLines)): 
        line = allLines[i]
        split = line.split('\t')
        timeElapsed = convertTime(split[2])
        # i.e. [NYK 11-12]
        
        scoreUpdate = re.search(score, line)
        if scoreUpdate != None:
            # Update time seris
            team, firstScore, secondScore = scoreUpdate.groups()
            otherTeam = teams[0] if team == teams[1] else teams[1]

            scores[team].append(int(firstScore))
            scores[otherTeam].append(int(secondScore))
            
            allTimes.append(timeElapsed)

    #diffSeries = [s0 - s1 for s0, s1 in zip(scores[teams[0]], scores[teams[1]])]
    timeline = TimeLine(allTimes, scores)

    return teams, timeline, game_date


def writeTeamTS(times, scores, teams, outFile = 'oneSeries.csv'):
    ''' Note that scores are with respect to teams[0] - teams[1] '''
    out = open(outFile, 'w')
    out.write(teams[0] + ' ' + teams[1] + '\n')
    out.write('time, diff\n')

    for t, s in zip(times, scores):
        out.write(str(t) + ', ' + str(s) + '\n')
    out.close()

def convertTime(fileTime):
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
        date = g.date
        tl = g.timeline
        # Could use sets here instead
        other_team = tl.teams[0] if tl.teams[1] == team else tl.teams[1]
        file_name = team + '/' + date + '-' + other_team + '.csv'
        differential = tl.get_diff(team)
        write_one_game_to_file(file_name, tl.times, differential)

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





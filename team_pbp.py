# Nick Jones

import re
import math


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


def readAllGames(fileName = 'first5000.txt'):
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

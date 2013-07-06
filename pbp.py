# Nick Jones

import re
import math


'''
TODO: 
- players re-enter at start of new quarters
- one pass through to get every player who scored -- ignore others? Sure. 
'''

GAME_LENGTH = 48

def processGame():
    times, diffs, teams, playerTS = parseTimeline()
    writeTeamTS(times, diffs, teams)

def parseTimeline(fileName = '/Users/nickjones/Documents/Datasets/playbyplay2011_2012/onegame.txt'):
    f = open(fileName, 'r')
    allLines = f.readlines()
    f.close()

    # Last 6 characters of first column correspond to two teams playing
    teamStr = allLines[1].split()[0][-6:]
    teams = (teamStr[:3], teamStr[3:])

    # Time series for each team
    allTimes = []
    scores = dict(zip(teams, [[], []]))

    # { team -> set([p1, p2, ...])}
    allPlayers = getAllPlayers(allLines, teams)
    # Time series for each player
    # {Team -> {Player -> [<1 or 0 if on court at given time>]}}
    
    playerTimeSeries = {}
    for t in teams:
        playerTimeSeries[t] = {}
        curPlayers = allPlayers[t]
        for p in curPlayers:
            playerTimeSeries[t][p] = []
    print playerTimeSeries
        
    # Time Series of players (i.e. who is playing at each time)
    # {team -> [setOf5, setOf5, ...]}
    onCourt = dict(zip(teams, [set(), set()]))
    
    # Parse lines for scores, player whos scored, and when substitutions occur
    score = r'\[([A-z]{3})\s(\d*)\-(\d*)\]'
    nameScore = score + r"\s([A-z\'\"\-]*)"
    subOccur = r'\[([A-z]{3})\]\s(.*)\s(Substitution\sreplaced\sby\s)(.*)'
    quarterEnd = r'End of\s(.*)'

    for i in range(1, len(allLines)): 
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

            # Player who scored
            nameMatch = re.search(nameScore, line)
            if nameMatch != None:
                scorer = nameMatch.groups()[-1]
                if scorer not in onCourt[team]:
                    fixPastLineup(scorer, team, playerTimeSeries, timeElapsed, allTimes)
                onCourt[team].add(scorer)

            # Update all player time series
            for team, playersOnCourt in onCourt.iteritems():
                for p in allPlayers[team]:
                    if p in playersOnCourt:
                        playerTimeSeries[team][p].append(1) 
                    else:
                        playerTimeSeries[team][p].append(0) 
                
            '''    
            ## DEBUG ##
            if len(onCourt[teams[0]]) != 5:
                print i
                print teams[0], onCourt
            if len(onCourt[teams[1]]) != 5:
                print i
                print teams[1], onCourt
            ## DEBUG ##
            '''
            # Sub re

        # START OVER AT QUARTERS
        subHappened = re.search(subOccur, line)
        if subHappened != None:
            print 'Sub at line', i
            # If player replaced was not current <onCourt>, then must have started
            # most recent quarter. Update his time series to reflect this
            playerToUpdate, hisTeam = updateFive(subHappened, onCourt)
            if playerToUpdate != None:
                fixPastLineup(playerToUpdate, hisTeam, playerTimeSeries, timeElapsed, allTimes)

        # End of quarter, so remove all players from five on court
        endOfQuarter = re.search(quarterEnd, line)
        if endOfQuarter != None:
            for t in onCourt:
                onCourt[t].clear()

        #print '--------\n'



    # Time series of point differential 
    diffSeries = [s0 - s1 for s0, s1 in zip(scores[teams[0]], scores[teams[1]])]
    return allTimes, diffSeries, teams, playerTimeSeries




def fixPastLineup(player, team, timeSeries, curTime, allTimes):
    lastQuarterTime = getLastQuarter(curTime)
    print 'Last quarter time', lastQuarterTime
    seriesToUpdate = timeSeries[team][player]
    print 'Before', timeSeries[team][player]
    for t in range(len(timeSeries[team][player])):
        if allTimes[t] > lastQuarterTime:
            timeSeries[team][player][t] = 1
    print 'After', timeSeries[team][player]
    print '-----'


def updateFive(reMatch, onCourt):
    '''
    Update the <onCourt> set for given team 
    Returns None if player replaced was in current <onCourt>
    Returns name of player, if he was not in current <onCourt>
    '''
    team, playerOut, ignore, playerIn = reMatch.groups()
    playerOut, playerIn = playerOut.strip(), playerIn.strip()

    onCourt[team].add(playerIn)
    if playerOut in onCourt[team]:
        onCourt[team].remove(playerOut)
        return None, None
    return playerOut, team

def getLastQuarter(curTime):
    timeRoundedDown = int(math.ceil(curTime))
    lastQuarterTime = (timeRoundedDown / 12) * 12
    print 'Checking', curTime, lastQuarterTime
    return lastQuarterTime


def sanityCheck():
    times, diffs, teams, playerTS = parseTimeline('/Users/nickjones/Documents/Datasets/playbyplay2011_2012/onequarter.txt')
    for team, players in playerTS.iteritems():
        for i in range(len(times)):
            onFloor = sum([p[i] for p in players.values()])
            if onFloor != 5:
                print onFloor

def checkFives():
    times, diffs, teams, playerTS = parseTimeline('/Users/nickjones/Documents/Datasets/playbyplay2011_2012/onegame.txt')
    print 'Num time slots', len(times)
    for team, players in playerTS.iteritems():
        for i in range(len(times)):
            onFloor = sum([p[i] for p in players.values()])
            if onFloor != 5:
                print onFloor, team, 'at time', times[i] 
                print [p for p in players if players[p][i] == 1]
            print '-----'


def parsePlayerTimes(allLines, teams):
    onCourt = dict(zip(teams, [set(), set()]))
    for line in allLines:
        subOccur = r'\[([A-z]{3})\]\s(.*)\s(Substitution\sreplaced\sby\s)(.*)'
        m = re.search(subOccur, line)
        if m != None:
            team, playerOut, ignore, playerIn = m.groups()
            playerOut, playerIn = playerOut.strip(), playerIn.strip()
            if len(onCourt[team]) < 5:
                onCourt[team].add(playerIn)
            if playerOut in onCourt[team]:
                onCourt[team].remove(playerOut)
            print team
            print playerOut
            print playerIn
            print onCourt
            print '----\n'

def getAllPlayers(allLines, teams):
    ''' Loop over all events, parse every player who scored or was involved in a sub'''
    score = r'\[([A-z]{3})\s(\d*)\-(\d*)\]'
    nameScore = score + r"\s([A-z\'\"\-]*)"
    subOccur = r'\[([A-z]{3})\]\s(.*)\s(Substitution\sreplaced\sby\s)(.*)'
    # { team -> set([p1, p2, ...])}
    players = dict(zip(teams, [set(), set()]))
    for line in allLines:
        scoreMatch = re.search(nameScore, line)
        if scoreMatch != None:
            team, score1, score2, scorer = scoreMatch.groups()
            scorer = scorer.strip()
            players[team].add(scorer)
        subMatch = re.search(subOccur, line)
        if subMatch != None:
            team, playerOut, ignore, playerIn = subMatch.groups()
            playerIn = playerIn.strip()
            playerOut = playerOut.strip()
            players[team].add(playerIn)
            players[team].add(playerOut)

    return players

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

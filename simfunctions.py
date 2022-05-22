#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: josephoconnell
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

def date_input():
    
    # a function that asks for the date after the user runs the program
    
    month = int(input("Month (numerical): "))
    day = int(input("Day: "))
    year = int(input("Year: "))
    print()
    
    return([month,day,year])
    

def polish_games(df,nba = True):
    
    # assigning winners and losers to each game in dataframe
    
    winners = []

    ngames = len(df)
    
    for i in range(ngames):
        
        if df['Home Score'][i] > df['Away Score'][i]:
            
            winners.append(df['Home Team'][i])
            
        elif df['Home Score'][i] < df['Away Score'][i]:
            
            winners.append(df['Away Team'][i])
            
        else:
            
            winners.append(YTP)
            
    # standardizing game scores to only regulation time
            
    home_adj, away_adj = [],[]
    
    if nba == True:
        
        minutes = 48
    
    else:
        
        minutes = 40
    
    for i in range(ngames):
        
        n = df['Overtime Periods'][i]
        
        if n > 0:        
            
            home = round(df['Home Score'][i] * minutes/(minutes + 5 * n), 2)
            away = round(df['Away Score'][i] * minutes/(minutes + 5 * n), 2)
            
        else:
            
            home = df['Home Score'][i]
            away = df['Away Score'][i]
            
        home_adj.append(home)
        away_adj.append(away)
        
    # adding margin of victories to each row of the data frame
        
    margin_of_victory = []

    for i in range(ngames):
            
        if df['Home Score'][i] > df['Away Score'][i]:
            
            margin_of_victory.append(int(df['Home Score'][i] - df['Away Score'][i]))
            
        elif df['Home Score'][i] < df['Away Score'][i]:
            
            margin_of_victory.append(int(df['Away Score'][i] - df['Home Score'][i]))
            
        else:
            
            margin_of_victory.append(0)
    
    df['winner'] = winners
    df['Home Adj'] = home_adj
    df['Away Adj'] = away_adj
    df['Margin of Victory'] = margin_of_victory

def game_log(team,df,n = 0):
    
    #subsetting dataframe to only grab games for a particular team
    
    gamelog = df[(df['Home Team'] == team)|(df['Away Team'] == team)]
    gamelog = gamelog[gamelog['winner'] != YTP]
    
    if n != 0:
        
        gamelog = gamelog.tail(n)
    
    return(gamelog)

def nights_slate1(date,df):
    
    #subsetting the dataframe to one day's worth of games
    #useful for later functions
    
    slate = df[['Home Team','Away Team']][(df['Month'] == date[0]) & (df['Day'] == date[1]) & (df['Year'] == date[2])]
    return(slate)
    
def sim_game_gauss_rates(home,away,df,spread,nba = True,iterations = 100, lag = 10,printout = True,graph = True):

    # grabbing the game logs of the home and away teams
    homegames = game_log(home,df,lag).reset_index()
    awaygames = game_log(away,df,lag).reset_index()
    
    # calculating mu and sigma for the last XXX amount of games 
    homescores = []
    homepag = []
    awayscores = []
    awaypag = []
    
    for i in range(lag):
                
        if homegames['Home Team'][i] == home:
            homescores.append(homegames['Home Adj'][i])
            homepag.append(homegames['Away Adj'][i])
        else:
            homescores.append(homegames['Away Adj'][i])
            homepag.append(homegames['Home Adj'][i])
        
        if awaygames['Home Team'][i] == away:
            awayscores.append(awaygames['Home Adj'][i])
            awaypag.append(awaygames['Away Adj'][i])
        else:
            awayscores.append(awaygames['Away Adj'][i])
            awaypag.append(awaygames['Home Adj'][i])
            
    home_mu = np.mean(homescores)
    home_sigma = np.std(homescores)
    
    away_mu = np.mean(awayscores)
    away_sigma = np.std(awayscores)
    
    # adding a shift of the mean to allow some influence of the opponent's defense
    if nba == True:
        
        league_avg = nba_league_avg
        
    else:

        league_avg = wnba_league_avg
    
    defensive_handicap_home = league_avg - np.mean(homepag)
    defensive_handicap_away = league_avg - np.mean(awaypag)
    
    home_mu -= defensive_handicap_away
    away_mu -= defensive_handicap_home
    
    # running simulations 
    homewins = 0
    awaywins = 0
    homecovers = 0
    awaycovers = 0

    for i in range(iterations):
        
        #setting seeds for repeatability
        
        random.seed(i)
        
        home_i = random.normalvariate(home_mu,home_sigma)
        away_i = random.normalvariate(away_mu,away_sigma)
        
        #logic to determine winner and score of simulation
        
        if home_i > away_i:
            homewins += 1
        else:
            awaywins += 1
            
        if spread < 0:
            
            if home_i + spread > away_i:
                
                homecovers += 1
                
                
            else:
                
                awaycovers += 1
                
        elif spread > 0:
                
            if home_i > away_i - spread:
                
                homecovers += 1
                
            else:
                
                awaycovers += 1
                
    #give win and cover information as rates independent on the number of simulations
        
    home_wp = homewins/iterations
    away_wp = awaywins/iterations
    
    home_cp = homecovers/iterations
    away_cp = awaycovers/iterations
    
    if printout == True:
    
        print('The', home, 'won', str(round(home_wp * 100,1)) + '% of', iterations, 'simulated games.')
        print('The', away, 'won', str(round(away_wp * 100,1)) + '% of', iterations, 'simulated games.')
        
        if spread != 0:
        
            print('The', home, 'covered a', spread,'point spread in', str(round(home_cp * 100,1)) + '% of', iterations, 'simulated games.')
            print('The', away, 'covered a', spread * -1,'point spread in', str(round(away_cp * 100,1)) + '% of', iterations, 'simulated games.')
        
    if graph == True:
        
        # these bar graphs show the results of the simulations 
        
        if spread != 0:
        
            plt.bar([home + " Wins",away + " Wins",home + " Covers",away + " Covers"],[homewins,awaywins,homecovers,awaycovers])
            plt.title(home + " vs " + away + " in " + str(iterations) + " simulations with a spread of " + str(spread) + ".")
        
        else: 
            
            plt.bar([home + " Wins",away + " Wins"],[homewins,awaywins])
            plt.title(home + " vs " + away + " in " + str(iterations) + " simulations.")
        
        
        plt.show()
    
    if spread != 0:
    
        return(home_wp,away_wp,home_cp,away_cp)
    
    else:
        
        return(home_wp,away_wp)
    
def team_cover_spread(team,df,spread):
    
    teams_games = game_log(team,df)
    
    if spread < 0:
        
        # when the team is favored it is good to look at how much they win by
        
        wins = teams_games[teams_games['winner'] == team]
        
        plt.hist(wins['Margin of Victory'][wins['Margin of Victory'] > -1 * (spread)], color = 'green', label = 'Cover',bins = range(40))
        plt.hist(wins['Margin of Victory'][wins['Margin of Victory'] < -1 * (spread)], color = 'red', label = 'No Cover',bins = range(40))
        plt.hist(wins['Margin of Victory'][wins['Margin of Victory'] == -1 * (spread)], color = 'black', label = 'Push',bins = range(40))
        plt.xlim(0,40)
        plt.legend()
        plt.title(team + ' Margins of Victory')
        plt.show()
        
        cover_rate = len(wins[wins['Margin of Victory'] >  -1 * (spread)])/len(wins)
        
        print('The ' + team + ' have covered an ' + str( (spread)) + ' point spread in ' +  str(round(round(cover_rate,3) * 100,1)) + '% of '+ str(len(wins)) +' wins.' )
        
    else:
        
        # when the team is not favored it is good to look at how much they lose by
        
        losses = teams_games[(teams_games['winner'] != team) & (teams_games['winner'] != YTP)]
    
        plt.hist(losses['Margin of Victory'][losses['Margin of Victory'] < (spread)], color = 'green', label = 'Cover',bins = range(40))
        plt.hist(losses['Margin of Victory'][losses['Margin of Victory'] > (spread)], color = 'red', label = 'No Cover',bins = range(40))
        plt.hist(losses['Margin of Victory'][losses['Margin of Victory'] == (spread)], color = 'black', label = 'Push',bins = range(40))
        plt.xlim(0,40)
        plt.legend()
        plt.title(team + ' Margins of Victory')
        plt.show()
    
        cover_rate = len(losses[losses['Margin of Victory'] < spread])/len(losses)
        
        print('The ' + team + ' have covered an ' + str(spread) + ' point spread in ' +  str(round(round(cover_rate,3) * 100,1)) + '% of ' + str(len(losses)) +' losses.' )
    
    return



def game_cover_spread(home,away,df,spread):
    
    #spread is always input as away - home so it can be negative
    if spread > 0:
        # road team favorite
        team_cover_spread(away,df, -1 * spread)
        team_cover_spread(home,df, spread)
        
    else:
        # home team favorite
        team_cover_spread(away,df, -1 * spread)
        team_cover_spread(home,df, spread)
        
    return
    

def sim_slate_gauss(date,df,nba = True,lag = 10):
    
    tonights_games = nights_slate1(date,df).reset_index()
    
    output = pd.DataFrame({'Home': tonights_games['Home Team'],'Away': tonights_games['Away Team']})
    
    homewin = []
    awaywin = []
    homecover = []
    awaycover = []
    spreads = []
    
    for i in range(len(tonights_games)):
        
        spread = float(input(tonights_games['Away Team'][i] + " minus " + tonights_games['Home Team'][i] + ":"))
        print()            
        simmed = sim_game_gauss_rates(tonights_games['Home Team'][i],tonights_games['Away Team'][i],df,spread,nba,lag = lag)
        print()
        game_cover_spread(tonights_games['Home Team'][i],tonights_games['Away Team'][i],df,spread = spread)
        
        homewin.append(simmed[0])
        awaywin.append(simmed[1])
        spreads.append(spread)
        homecover.append(simmed[2])
        awaycover.append(simmed[3])
        
       
    output['Home Win Rate'] = homewin
    output['Away Win Rate'] = awaywin
    output['Spread'] = spreads
    output['Home Cover Rate'] = homecover
    output['Away Cover Rate'] = awaycover
    
    return(output)

YTP = 'Yet to Play'

nba_season = pd.read_csv('NBA Game Log.csv')
wnba_season = pd.read_csv('WNBA Game Log.csv')

polish_games(nba_season)
polish_games(wnba_season)

# creating important constants to be used in calculations above specifically in determining defensive handicap

nba_ngames_played = len(nba_season[nba_season['winner'] != YTP])
nba_home_avg = round(sum(nba_season['Home Adj'][nba_season['winner'] != YTP])/nba_ngames_played,3)
nba_away_avg = round(sum(nba_season['Away Adj'][nba_season['winner'] != YTP])/nba_ngames_played,3)
nba_league_avg = round((nba_home_avg + nba_away_avg)/2,3)

wnba_ngames_played = len(wnba_season[wnba_season['winner'] != YTP])
wnba_home_avg = round(sum(wnba_season['Home Adj'][wnba_season['winner'] != YTP])/wnba_ngames_played,3)
wnba_away_avg = round(sum(wnba_season['Away Adj'][wnba_season['winner'] != YTP])/wnba_ngames_played,3)
wnba_league_avg = round((wnba_home_avg + wnba_away_avg)/2,3)
    





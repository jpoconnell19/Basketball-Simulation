#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: josephoconnell
"""
# importing functions from helper file for the elimination of clutter
from simfunctions import *

def main():
    
    #get date information from user
    thedate = date_input()

    wnba_sims = sim_slate_gauss(thedate,wnba_season,nba = False, lag = 3)
    
    nba_sims = sim_slate_gauss(thedate,nba_season, lag = 5)

if __name__ == "__main__":
    main()





# -*- coding: utf-8 -*-
"""
Spyder Editor


This is the main file
"""
import pandas as pd
import excel_module as em
import website_scraper as ws
import stat_helper as sh
from deckmodule import Deck
import openpyxl as oxl
import requests
import numpy as np
from bs4 import BeautifulSoup as bs


# Excel Scraping, It will produce 3 excel files. FilteredDecks_View, FilteredDecks_Data, and Statistics and Breakdown
# Input : Excel sheet from SVO
# Requirements :    - all names and decklist must be inside 'Sheet1'
#                   - columns name , deck 1, deck 2, deck 3 must exists
#                   - decklists must end with ?lang=en or &lang=en


# ws.SVO_initial_scraper('Excel_and_CSV/IgnideusHalloween.xlsx')


# Post SVO scraping, It will produce 2 excel files. FilteredDecks_View, and Post_SVO_Data
# Input : JSON hashes from battlefy
# Requirements :    - SVO_Initial_Scraper must be ran, FilteredDecks_View contains all participants lineups
#                   - JSON hash must be valid
#                   - People changing name after tournament ended will skew the results
# Example : https://battlefy.com/shadowverse-open/svo-seao-monthly-cup-september/5f02c8825522b86652930ae3/stage/5f6574dd1104cd7a261297b9/bracket/7
# 5f02c8825522b86652930ae3 is tourneyhash and 5f6574dd1104cd7a261297b9 is stagehash

# bfy_tourneyhash = '5f02c8825522b86652930ae3'
# bfy_stagehash = '5f6574dd1104cd7a261297b9'
# ws.SVO_posttourney_scraper(bfy_tourneyhash, bfy_stagehash)



# Other Website Scraping : JCG, MSCUP, It will produce 3 excel files. FilteredDecks_View, FilteredDecks_Data, and Statistics and Breakdown
# Input : Json page from respective website
# Requirements :    - JSON link must be valid

tcode = ws.JCG_latest_tourney('rotation', 'group')
json = 'https://sv.j-cg.com/compe/view/entrylist/' + tcode + '/json'
ws.JCG_scraper(json)

# ws.manasurge_bfy_scraper('https://dtmwra1jsgyb0.cloudfront.net/tournaments/5f7b4e720ee5b43873159b96/teams')

# Quick Groupstage check for JCG
# Input : JCG page for specified tourney (not top 16)
# Requirements : JCG_Scraper for specified tourney needs to be ran first

# name = ws.JCG_group_winner_check('https://sv.j-cg.com/compe/view/tour/2471')  
# count = sh.deck_quick_count(name)

# DSAL_scraper('http://www.littleworld.tokyo/RoundOfDarkness/openingPartySecond')


# Ban Analyzer
# Input : JSON Hashes, player name

# bfy_tourneyhash = '5f02c8825522b86652930ae3'
# bfy_stagehash = '5f6574dd1104cd7a261297b9'
# player = 'TK 雪見小梅'

# stats = ws.SVO_ban_peek(player, bfy_tourneyhash, bfy_stagehash)


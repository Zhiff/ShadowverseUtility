# -*- coding: utf-8 -*-
"""
Spyder Editor


This is the main file
"""
import pandas as pd
import excel_module as em
import website_scraper as ws
import stat_helper as sh
import t2_stats as t2
import jcg_helper as jcg
from deckmodule import Deck
import openpyxl as oxl
import requests
import numpy as np
from bs4 import BeautifulSoup as bs
import time

start_time = time.time()
# Excel Scraping, It will produce 3 excel files. FilteredDecks_View, FilteredDecks_Data, and Statistics and Breakdown
# Input : Excel sheet from SVO
# Requirements :    - all names and decklist must be inside 'Sheet1'
#                   - columns name , deck 1, deck 2, deck 3 must exists
#                   - decklists must end with ?lang=en or &lang=en

# em.convertSVOformat('Excel_and_CSV/SVOMarchWEST.xlsx')
# ws.SVO_initial_scraper('Excel_and_CSV/SVO.xlsx')

# ws.SVO_initial_scraper('Excel_and_CSV/svot8.xlsx')


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


tcode = ws.JCG_latest_tourney('rotation', 'top16')
ws.JCG_scraper(tcode)



# ws.manasurge_bfy_scraper('https://dtmwra1jsgyb0.cloudfront.net/tournaments/5f7b4e720ee5b43873159b96/teams')

# Quick Groupstage check for JCG
# Input : JCG page for specified tourney (not top 16)
# Requirements : JCG_Scraper for specified tourney needs to be ran first

# tcode = '2474'
# tour = 'https://sv.j-cg.com/compe/view/tour/' + tcode
# name = ws.JCG_group_winner_check(tour)  
# count = sh.deck_quick_count(name)

# ws.DSAL_scraper('http://www.littleworld.tokyo/RoundOfDarkness/openingPartySecond')


# Ban Analyzer
# Input : JSON Hashes, player name

# bfy_tourneyhash = '5f02c8825522b86652930ae3'
# bfy_stagehash = '5f6574dd1104cd7a261297b9'
# player = 'TK 雪見小梅'

# stats = ws.SVO_ban_peek(player, bfy_tourneyhash, bfy_stagehash)


# JCG T2 Website Scaping: It will produce 1 excel file
# Input : links of JCG T2 qualifying and final tourney (2 links)
# If bug occurs: (e.g. sv.j-cg.com/compe/view/match/2481/528568/) a report is printed and manual fix is needed. 

# tcodes = [ws.JCG_latest_tourney('2pick', 'group'), ws.JCG_latest_tourney('2pick', 'top16')]
# t2.JCG_T2_scraper(tcodes)


#JCG Trends
# Input : lists of JCG IDs

# jcgids, dates = jcg.scrapseasonIDs('rotation', '16th Season')
# ws.generate_archetype_trends(jcgids, dates)

# url = 'https://rage-esports.jp/shadowverse/2021spring/pre/deck2'
# source = requests.get(url).text
# soup = bs(source, 'lxml')
# filtered = soup.find_all('td', bgcolor='white')
# name1 = []
# deck1 = []
# deck2 = []
# for lit in filtered[::3]:
#     name = lit.text
#     name1.append(name)
# for lit in filtered[1::3]:
#     lits = lit.find('a')
#     name = lits.get('href')
#     deck1.append(name)
# for lit in filtered[2::3]:
#     lits = lit.find('a')
#     name = lits.get('href')
#     deck2.append(name)    

# db = np.column_stack((name1,deck1,deck2))
# df = pd.DataFrame(db)
# df = df.rename(columns={0:'name', 1:'deck 1', 2:'deck 2'})

# writer = pd.ExcelWriter('Excel_and_CSV/rage.xlsx')
# df.to_excel(writer, index=False)
# writer.save()
    
    
# alllink = filtered.find_all('a')
# for link in alllink[::2]:
#     store = link.get('href')
#     deck1.append(store)
# for link in alllink[1::2]:
#     store = link.get('href')
#     deck2.append(store)

# db = np.column_stack((deck1,deck2))
# df = pd.DataFrame(db)
# df = df.rename(columns={0:'deck 1', 1:'deck 2'})

# writer = pd.ExcelWriter('Excel_and_CSV/JCG_Raw.xlsx')
# df.to_excel(writer, index=False)
# writer.save()

# print(filtered)
print("--- %s seconds ---" % (time.time() - start_time))
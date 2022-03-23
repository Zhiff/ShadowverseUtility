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
import json

start_time = time.time()
# Excel Scraping, It will produce 3 excel files. FilteredDecks_View, FilteredDecks_Data, and Statistics and Breakdown
# Input : Excel sheet from SVO
# Requirements :    - all names and decklist must be inside 'Sheet1'
#                   - columns name , deck 1, deck 2, deck 3 must exists
#                   - decklists must end with ?lang=en or &lang=en

# em.convertSVOformat('Excel_and_CSV/MaySEAO.xlsx')
# ws.SVO_initial_scraper('Excel_and_CSV/Weekend.xlsx')

# ws.SVO_initial_scraper('Excel_and_CSV/SAO.xlsx')

# tcode1 = 'Ny1fDVSBlfho'
# tcode2 = 'i2nJD0c4zoaA'

# df = pd.read_excel('Excel_and_CSV/JCG_Raw.xlsx')


# resultpage = 'https://sv.j-cg.com/competition/' + tcode1 + '/results'
# source = requests.get(resultpage).text
# soup = bs(source, 'lxml')

# names1 = []

# qualified = soup.find_all('div', class_='result-name')
# for user in qualified:
#         # Add their name into array
#         name = user.text
#         names1.append(name)
        
# resultpage = 'https://sv.j-cg.com/competition/' + tcode2 + '/results'
# source = requests.get(resultpage).text
# soup = bs(source, 'lxml')

# names2 = []

# qualified = soup.find_all('div', class_='result-name')
# for user in qualified:
#         # Add their name into array
#         name = user.text
#         names2.append(name)

# allname = names1 + names2
# qual = pd.DataFrame(allname).rename(columns={0:'name'})

# data = qual.merge(df)

# data = data.rename(columns={'deck 1':'arc 1', 'deck 2':'arc 2'})
# top16 = data
# em.add_conversion_rate(top16)  

# em.add_class_color(1)

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
# Input : Format, Stage
# Requirements :    - JSON must be valid

comp_format = 'rotation'
stage = 'top16'
# tcode = ws.JCG_latest_tourney(comp_format, stage)
# ws.JCG_scraper(tcode)

tcode, status = ws.JCG_latest_tourney_with_status(comp_format, stage)

if status == 'Finished':
    if stage is 'top16':
        entry_df = jcg.get_deck_profile(tcode)
        matchids = jcg.gather_match_id(tcode, 'top16')
        P1, P2, resultP1, resultP2 = jcg.create_matches_dataset(matchids)
        jcg.publish_final_standings(entry_df, P1, P2, resultP1, resultP2)
    elif stage is 'group':
        entry_df = jcg.get_deck_profile(tcode)
        master_df, lineupdict = jcg.create_master_df(entry_df)
        matchids = jcg.gather_match_id(tcode, 'group')
        
        print("--- %s seconds ---" % (time.time() - start_time))
        
        P1, P2, resultP1, resultP2 = jcg.create_matches_dataset(matchids)
        
        print("--- %s seconds ---" % (time.time() - start_time))
        
        overall_view_df = jcg.get_overall_view(master_df, P1, P2, resultP1, resultP2)
        top16_df = jcg.get_top16_view(tcode)
        decks_df, class_df = jcg.get_deck_and_class_view(master_df)
        lineup_df = jcg.get_lineup_view(lineupdict, P1, P2, resultP1, resultP2)
        conv_df = jcg.get_top16_conversion_view(top16_df, decks_df)
        matchup_df = jcg.get_matchup_view(lineupdict, P1, P2, resultP1, resultP2)
        
        print("--- %s seconds ---" % (time.time() - start_time))
        
        ws.jcg_excel_finishing(master_df, top16_df, overall_view_df, decks_df, class_df, lineup_df, conv_df, matchup_df)

    





# ws.manasurge_bfy_scraper('https://dtmwra1jsgyb0.cloudfront.net/tournaments/5f7b4e720ee5b43873159b96/teams')

# Quick Groupstage check for JCG
# Input : JCG page for specified tourney (not top 16)
# Requirements : JCG_Scraper for specified tourney needs to be ran first

# tcode = '2474'
# tour = 'https://sv.j-cg.com/compe/view/tour/' + tcode
# name = ws.JCG_group_winner_check(tour)  
# count = sh.deck_quick_count(name)

# ws.DSAL_scraper('http://www.littleworld.tokyo/RoundOfDarkness/openingPartySecond')

# ws.SKO_Scraper('http://sko.uniqxp.com')



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

# jcgids, dates = jcg.scrapseasonIDs('rotation', '20th Season')
# ws.generate_archetype_trends(jcgids, dates)

# names = []
# deck1 = []
# deck2 = []
# for i in range(len(jcgids)):
#         ids = jcgids[i]
#         date = dates[i]
        
#         resultpage = 'https://sv.j-cg.com/competition/' + ids + '/results'
#         source = requests.get(resultpage).text
#         soup = bs(source, 'lxml')

            
#         firstplace = soup.find('div', class_='result result-1')
#         name = date
#         names.append(name)
#         # Add their decks into array
#         links = firstplace.find_all('a')
#         for link in links[1::3]:
#             decks = link.get('href')
#             deck1.append(decks)
#         for link in links[2::3]:
#             decks = link.get('href')
#             deck2.append(decks)
        
# df = pd.DataFrame([names,deck1,deck2]).transpose().rename(columns={0:'name', 1:'deck 1', 2:'deck 2'})    
# writer = pd.ExcelWriter('Excel_and_CSV/temp.xlsx')
# df.to_excel(writer, index=False)
# writer.save()

# ws.SVO_initial_scraper('Excel_and_CSV/temp.xlsx')

# Post Playoff

# url = 'https://rage-esports.jp/shadowverse/2022spring/pre/deck3'
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

# Pre Playoff

# url = 'https://rage-esports.jp/shadowverse/2022spring/pre/deck'
# source = requests.get(url).text
# soup = bs(source, 'lxml')
# filtered = soup.find_all('td', bgcolor='black')

# print (filtered)
# name1 = []
# deck1 = []
# deck2 = []
# for lit in filtered[1::4]:
#     name = lit.text
#     name1.append(name)
# for lit in filtered[2::4]:
#     lits = lit.find('a')
#     name = lits.get('href')
#     deck1.append(name)
# for lit in filtered[3::4]:
#     lits = lit.find('a')
#     name = lits.get('href')
#     deck2.append(name)    

# db = np.column_stack((name1,deck1,deck2))
# df = pd.DataFrame(db)
# df = df.rename(columns={0:'name', 1:'deck 1', 2:'deck 2'})

# writer = pd.ExcelWriter('Excel_and_CSV/rage.xlsx')
# df.to_excel(writer, index=False)
# writer.save()

#SVWGP
# url = 'https://esports.shadowverse.com/news/detail/198?lang=ja'
# source = requests.get(url).text
# soup = bs(source, 'lxml')


# namelist = []
# deck1 = []
# deck2 = []
# deck3 = []
# #player name handling
# playerlist = soup.find_all('td', class_='player')
# for player in playerlist:
#     name = player.text.replace("\n","")
#     namelist.append(name)

#decklist handling
# table = soup.find('div', class_='ranking')
# decklist = table.find_all('a')
# for deckid in decklist[0::3]:
#     deck = deckid.get('href')
#     deck1.append(deck)
# for deckid in decklist[1::3]:
#     deck = deckid.get('href')
#     deck2.append(deck)
# for deckid in decklist[2::3]:
#     deck = deckid.get('href')
#     deck3.append(deck)

# db = np.column_stack((namelist,deck1,deck2,deck3))
# df = pd.DataFrame(db)
# df = df.rename(columns={0:'name', 1:'deck 1', 2:'deck 2', 3:'deck 3'})

# writer = pd.ExcelWriter('Excel_and_CSV/WGPDay.xlsx')
# df.to_excel(writer, index=False)
# writer.save()

# for player in playerlist:
#     links = player.find_all('li')
#     for link in links:
        
#         deck = link.find('a').get('href')
#         tempdeck.append(deck)
        
# decklist = soup.find_all('a')

# link = []
# for deck in decklist:
#     lits = deck.get('href')
#     link.append(lits)

# df = pd.DataFrame(link)
# writer = pd.ExcelWriter('Excel_and_CSV/aaa.xlsx')
# df.to_excel(writer, index=False)
# writer.save()


# for a in namelist:
#     name = a.text
#     name1.append(name)

# tcode = 'Z5sQN9tYjwKn'
# entrieslink = 'https://sv.j-cg.com/competition/' + tcode + '/entries'
# source = requests.get(entrieslink).text
# soup = bs(source, 'lxml')
    
# # Find and extract JSON file in HTML
# all_scripts = soup.find_all('script')
    
# #currently hardcasted, faster processing but will be screwed when website changes
# dljson = all_scripts[7].string
    
# #cleaning string to comply with JSON format
# cleanedjson = dljson[dljson.find('list'):dljson.find('listFiltered')]
# finaljson = cleanedjson.replace('list:','').strip()[:-1]
    
# data = json.loads(finaljson)
# jsondf = pd.DataFrame(data)

# sv = 'https://shadowverse-portal.com/deck/'
# lang_eng = '?lang=en'
# data1 = jsondf.loc[jsondf['result']==1].reset_index().copy()
# team = pd.DataFrame(list(data1['users'])) 
# user1data = pd.DataFrame(list(team[0]))
# user2data = pd.DataFrame(list(team[1]))

# user1data['d1'] = user1data['sv_decks'].apply(lambda x: x[0]['hash'] if x else None)
# user2data['d2'] = user2data['sv_decks'].apply(lambda x: x[0]['hash'] if x else None)
# user1data['deck 1']= user1data['d1'].apply(lambda x: sv + x + lang_eng if x else 'Invalid Deck')
# user2data['deck 2']= user2data['d2'].apply(lambda x: sv + x + lang_eng if x else 'Invalid Deck')
# user1dataf = user1data[['name','deck 1']].copy().rename(columns={'name':'player 1'})
# user2dataf = user2data[['name','deck 2']].copy().rename(columns={'name':'player 2'})

# df3 = pd.concat([data1,user1dataf,user2dataf], axis=1)
# df = df3[['name','player 1','player 2','deck 1','deck 2']].copy()

# writer = pd.ExcelWriter('Excel_and_CSV/JCG_DoublesRaw.xlsx')
# df.to_excel(writer, index=False)
# writer.save()

# ws.SVO_initial_scraper('Excel_and_CSV/JCG_DoublesRaw.xlsx')

# data3 = sh.handle_duplicate_row(data2, 'name').reset_index().drop(['index'], axis=1)

# url = 'https://rage-esports.jp/shadowverse/2022spring/pre/deck'
# source = requests.get(url).text
# soup = bs(source, 'lxml')
# filtered = soup.find_all('td')

# print (filtered)
# name1 = []
# deck1 = []
# deck2 = []

# for lit in filtered[5::4]:
#     name = lit.text
#     name1.append(name)
# for lit in filtered[6::4]:
#     lits = lit.find('a')
#     name = lits.get('href')
#     deck1.append(name)
# for lit in filtered[7::4]:
#     lits = lit.find('a')
#     name = lits.get('href')
#     deck2.append(name)    

# db = np.column_stack((name1,deck1,deck2))
# df = pd.DataFrame(db)
# df = df.rename(columns={0:'name', 1:'deck 1', 2:'deck 2'})

# writer = pd.ExcelWriter('Excel_and_CSV/rage.xlsx')
# df.to_excel(writer, index=False)
# writer.save()


print("--- %s seconds ---" % (time.time() - start_time))


# print("--- %s seconds ---" % (time.time() - start_time))
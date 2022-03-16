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
# ws.SVO_initial_scraper('Excel_and_CSV/rage.xlsx')

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


# tcode = ws.JCG_latest_tourney('rotation', 'top16')
# ws.JCG_scraper(tcode)


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

# jcgids, dates = jcg.scrapseasonIDs('rotation', '19th Season')
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


print('Start')
# tcode = 'EfKBukcCf4Lp' #Full Top16
# tcode = '87sQDLai1JUy' #Missing entry top16
tcode = 'gVjDGKNATejd' # Full Group Stage
# tcode = 'ndFBjj5bpUbt'

top16view_df = jcg.group_winner_check_2(tcode)

#Entry Gathering and Preparation

entrieslink = 'https://sv.j-cg.com/competition/' + tcode + '/entries'
source = requests.get(entrieslink).text
soup = bs(source, 'lxml')
# Find and extract JSON file in HTML
all_scripts = soup.find_all('script')
#currently hardcasted, faster processing but will be screwed when website changes
dljson = all_scripts[7].string
#cleaning string to comply with JSON format
cleanedjson = dljson[dljson.find('list'):dljson.find('listFiltered')]
finaljson = cleanedjson.replace('list:','').strip()[:-1]
data = json.loads(finaljson)
jsondf = pd.DataFrame(data)

print("--- %s seconds ---" % (time.time() - start_time))

sv = 'https://shadowverse-portal.com/deck/'
jcg = 'https://sv.j-cg.com/user/'
lang_eng = '?lang=en'
data1 = jsondf.loc[jsondf['result']==1].copy()
data1['d1'] = data1['sv_decks'].apply(lambda x: x[0]['hash'] if x else None)
data1['d2'] = data1['sv_decks'].apply(lambda x: x[1]['hash'] if x else None)
data1['deck 1']= data1['d1'].apply(lambda x: sv + x + lang_eng if x else 'Invalid Deck')
data1['deck 2']= data1['d2'].apply(lambda x: sv + x + lang_eng if x else 'Invalid Deck')
data1['profile']=data1['nicename'].apply(lambda x: jcg + x)
data2 = data1[['profile','name','deck 1','deck 2']].copy()
data3 = sh.handle_duplicate_row(data2, 'name').reset_index().drop(['index'], axis=1)
df = data3

for i in range(1, 3):
    df[f'arc {i}'] = df[f'deck {i}'].apply(lambda x: Deck(x).archetype_checker())
for i in range(1, 3):
    df[f'class {i}'] = df[f'deck {i}'].apply(lambda x: Deck(x).class_checker())     
df = sh.add_lineup_column_2decks_class(df)
df = sh.add_lineup_column_2decks(df) # Base Entries : Filtered-Deck-Data

print("--- %s seconds ---" % (time.time() - start_time))
print("end of entry initialization")


# preparation for Lineup
dfc = df[['profile', 'Lineup']]
dfc = dfc.set_index('profile')
lineupdict = dfc.to_dict() 

#Collecting MatchIDs for Result pages
matchids = []

istop16 = False
#get info from the whole bracket
bracketpage = 'https://sv.j-cg.com/competition/' + tcode + '/bracket'
source = requests.get(bracketpage).text
soup = bs(source, 'lxml')
allscr = soup.find_all('script')

title = soup.find('div', class_='competition-title').text
if '決勝トーナメント' in title:
    istop16 = True

if (istop16):
    #Specify the exact JSON inside the bracket and cleaning up
    tjson = allscr[7].text
    cleanedjson = tjson[tjson.find('"groups":['):tjson.find('],"myUsername"')]
    finaljson = cleanedjson.replace('"groups":[','')
    bracketid = json.loads(finaljson)['id']
    bracketid = str(bracketid)

    bracketjson = 'https://sv.j-cg.com/api/competition/group/' + bracketid
    bracketresponse = requests.get(bracketjson)    
    bracketdata = bracketresponse.json()['rounds']
    for j in range(len(bracketdata)):
        groupdata = bracketdata[j]['matches']
        for k in range(len(groupdata)):
            matchid = groupdata[k]['id']
            matchids.append(str(matchid))
    
else:
    #Specify the exact JSON inside the bracket and cleaning up
    tjson = allscr[7].text
    cleanedjson = tjson[tjson.find('"groups":['):tjson.find('],"myUsername"')]
    finaljson = '{' + cleanedjson + ']}'
    bracket = json.loads(finaljson)
    # traverse the JSON to find each bracket ID , and furthermore match ID
    for i in range(16): #Groupstage has 16 group
        bracketid = bracket['groups'][i]['id']
        bracketid = str(bracketid)

        bracketjson = 'https://sv.j-cg.com/api/competition/group/' + bracketid
        bracketresponse = requests.get(bracketjson)    
        bracketdata = bracketresponse.json()['rounds']
        for j in range(len(bracketdata)):
            groupdata = bracketdata[j]['matches']
            for k in range(len(groupdata)):
                matchid = groupdata[k]['id']
                matchids.append(str(matchid))

print("--- %s seconds ---" % (time.time() - start_time))
print("end of MatchID gatherings")

#Collecting Matches Record
validmatch = []
P1 = []
P2 = []
ResultP1 = []
ResultP2 = []

for match in matchids:
    matchjson = 'https://sv.j-cg.com/api/competition/match/' + match
    matchresponse = requests.get(matchjson)
    matchdata = matchresponse.json()
    if len(matchdata['teams']) > 1: #Check if it is not a bye round
        validmatch.append(match)
        Player1 = 'https://sv.j-cg.com/user/' + matchdata['teams'][0]['nicename']
        P1.append(Player1)
        Player2 = 'https://sv.j-cg.com/user/' + matchdata['teams'][1]['nicename']
        P2.append(Player2)
        PR1 = matchdata['teams'][0]['won']
        ResultP1.append(PR1)
        PR2 = matchdata['teams'][1]['won']
        ResultP2.append(PR2)
        print("--- %s seconds ---" % (time.time() - start_time))
    else:
        Player1 = 'https://sv.j-cg.com/user/' + matchdata['teams'][0]['nicename']
        P1.append(Player1)
        P2.append(np.nan)
        PR1 = matchdata['teams'][0]['won']
        ResultP1.append(PR1)
        ResultP2.append(0)

print("Matches Dataset has been completed")

#View Creation
        
# 1. Qualified Top 16 and Overall Players View

# A. Wins Dataset Creation
Players = P1 + P2
Wins = ResultP1 + ResultP2
WinDS1 = pd.DataFrame([Players,Wins]).transpose().rename(columns={0:'profile', 1:'win'})
WinDS = WinDS1.groupby('profile')['win'].sum().reset_index().sort_values('win', ascending=False)

# Overall Players View

OverallP1 = pd.merge(df, WinDS, how='left').sort_values('win', ascending=False, ignore_index=True)
OverallP1['name'] = '=HYPERLINK("' + OverallP1['profile'] + '", "' + OverallP1['name'] + '")' 
OverallView_df = OverallP1[['name','deck 1','deck 2','win']]

print("Overall View Dataset is ready")

# Qualified Top16 View

# 2. Decks View

# Sum up Decks based on archetypes
decks = df.loc[:,'arc 1':'arc 2'].stack().value_counts(normalize = False, ascending = False)
decks = decks.rename_axis("Deck Archetype").reset_index(name = 'Count')
decks['Player %'] = (round((decks['Count']/(int(df.shape[0])))*100, 2))
decks_df = decks.copy()

# Sum up Decks based on class
classes = df.loc[:,'class 1':'class 2'].stack().value_counts(normalize = False, ascending = False)
classes = classes.rename_axis("Class").reset_index(name = 'Count')
classes['Player %'] = (round((classes['Count']/(int(df.shape[0])))*100, 2))
classes_df = classes.copy()

print("Deck and Class View Dataset is ready")

# 2. Lineup View

lds = pd.DataFrame(lineupdict)
lineup = lds["Lineup"].value_counts(normalize = False, ascending = False)
lineup = lineup.rename_axis("Lineup").reset_index(name = 'Count')
lineup['Player %'] = (round((lineup['Count']/(int(df.shape[0])))*100, 2))
lineup['Lineup'] = lineup.loc[:,'Lineup'].apply(lambda x: ' - '.join(x))

LineDS1 = WinDS.copy()
LineDS1['profile'] = LineDS1.loc[:,'profile'].apply(lambda x: lineupdict['Lineup'][x])
LineDS1['profile'] = LineDS1.loc[:,'profile'].apply(lambda x: ' - '.join(x))
LineDS1 = LineDS1.rename(columns={'profile':'Lineup'})
LineDS = LineDS1.groupby('Lineup')['win'].sum().reset_index().sort_values('win', ascending=False)

total1 = pd.DataFrame(Players).rename(columns={0:'profile'}).dropna()
total1['profile'] = total1.loc[:,'profile'].apply(lambda x: lineupdict['Lineup'][x])
total1['profile'] = total1.loc[:,'profile'].apply(lambda x: ' - '.join(x))
total1 = total1.rename(columns={'profile':'Lineup'})
total = total1['Lineup'].value_counts(ascending = False).reset_index().rename(columns={'index':'Lineup', 'Lineup':'total'})

LineupDS = pd.merge(LineDS, total, how='left')
LineupDS['lose'] = LineupDS['total']-LineupDS['win']
LineupDS['Winrate %'] = round(100 * LineupDS['win']/LineupDS['total'], 2)

LineupFinal = pd.merge(lineup, LineupDS, how='left')
LineupFinal['Lineup'] = LineupFinal.loc[:,'Lineup'].apply(lambda x: x.split(" - "))
LineupFinal[['Deck 1','Deck 2']] = pd.DataFrame(LineupFinal['Lineup'].to_list(), index=LineupFinal.index)
LineupFinal_df = LineupFinal[['Deck 1', 'Deck 2', 'Count', 'Player %','win','lose','Winrate %']]

print("Lineup View Dataset is ready")
print("--- %s seconds ---" % (time.time() - start_time))

# 3. Conversion Rate Page

#count deck and combine with data

conv_top16 = top16view_df.copy()
conv_top16['deck 1'] = conv_top16['deck 1'].apply(lambda x: Deck(x).archetype_checker())
conv_top16['deck 2'] = conv_top16['deck 2'].apply(lambda x: Deck(x).archetype_checker())
conv_decks = conv_top16.loc[:,'deck 1':'deck 2'].stack().value_counts(normalize = False, ascending = False)
conv_decks = conv_decks.rename_axis("Deck Archetype").reset_index(name = 'Count')
conv_decks['Top 16 Rep%'] = (round((conv_decks['Count']/(int(conv_top16.shape[0])))*100, 2))
whole_decksdf = decks_df.copy()
whole_decksdf = whole_decksdf.rename(columns={'Count':'Total', 'Player %':'Group Rep%'})
mergedeck = conv_decks.merge(whole_decksdf)
mergedeck['Conversion Rate %'] = round(mergedeck['Count']/mergedeck['Total'], 4)*100 
mergedeck = mergedeck.rename(columns={'Count':'Top 16', 'Total':'Group'})
mergedeck = mergedeck.astype(str)
mergedeck['Conversion Rate %'] = mergedeck['Conversion Rate %'].astype(float)
mergedeck['Top 16 (Player%)'] = mergedeck['Top 16'] + ' (' + mergedeck['Top 16 Rep%'] + '%)'
mergedeck['Group (Player%)'] = mergedeck['Group'] + ' (' + mergedeck['Group Rep%'] + '%)'
conv_page_df = mergedeck[['Deck Archetype','Top 16 (Player%)','Group (Player%)','Conversion Rate %']]
    

#Excel Things

outputfile = "Excel_and_CSV/Statistics and Breakdown.xlsx"
writer = pd.ExcelWriter(outputfile)

top16view_df.to_excel(writer, sheet_name='Qualified for Top 16', index=False, startrow = 0, startcol = 0)
OverallView_df.to_excel(writer, sheet_name='Names and Links', index=False, startrow = 0, startcol = 0)
decks_df.to_excel(writer, sheet_name='Decks', index=True, startrow = 0, startcol = 0)
classes_df.to_excel(writer, sheet_name='Decks', index=True, startrow = 0, startcol = 5)
LineupFinal_df.to_excel(writer, sheet_name='Lineup', index=True, startrow = 0, startcol = 0)
conv_page_df.to_excel(writer, sheet_name='Top 16 Conversion', index=True, startrow = 0, startcol = 0)


print("Start Working on Excel")
print("--- %s seconds ---" % (time.time() - start_time))

maxdeck = 2
em.tournament_breakdown(df, writer, maxdeck)  

writer.save()

print("Initial page Completed")
print("--- %s seconds ---" % (time.time() - start_time))


em.excel_convert_custom('Excel_and_CSV/Statistics and Breakdown.xlsx', 3, True)

print("Completed")
print("--- %s seconds ---" % (time.time() - start_time))
# # # 2. Matchup Dataset
# # Matchdf1 = pd.DataFrame([P1,ResultP1]).transpose().rename(columns={0:'profile', 1:'ResultP1'})
# # Matchdf2 = pd.DataFrame([P2,ResultP2]).transpose().rename(columns={0:'profile', 1:'ResultP2'})

# print("--- %s seconds ---" % (time.time() - start_time))



# Matchdf1 = Matchdf1.merge(df[['profile','Lineup']], on='profile')
# Matchdf1 = Matchdf1.rename(columns={'Lineup':'Lineup 1'})
# Matchdf1t = Matchdf1[['Lineup 1','ResultP1']].copy()
# Matchdf2 = Matchdf2.merge(df[['profile','Lineup']], on='profile')
# Matchdf2 = Matchdf2.rename(columns={'Lineup':'Lineup 2'})
# Matchdf2t = Matchdf2[['Lineup 2','ResultP2']].copy()
# Matchdfall = pd.concat([Matchdf1t, Matchdf2t],axis=1)

# print("--- %s seconds ---" % (time.time() - start_time))
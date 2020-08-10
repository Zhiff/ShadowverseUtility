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

# Excel Scraping : SVO

# em.excel_convert_quick(''excelfile'')
# ws.SVO_initial_scraper('Excel_and_CSV/SVO_WEST_AUGUST_FULL.xlsx')


# Website Scraping : JCG, MSCUP, SVO_Top
# ws.JCG_scraper('https://sv.j-cg.com/compe/view/entrylist/2341/json')
# ws.manasurge_bfy_scraper('https://dtmwra1jsgyb0.cloudfront.net/tournaments/5f1e79da534e897bd0c64673/teams')

#Updated for AUG WEST
# ws.SVO_tops_scraper_v1('https://dtmwra1jsgyb0.cloudfront.net/stages/5f2eb61c0ad5e05d5e217f8c/latest-round-standings')

# excel_convert_quick('Excel_and_CSV/SVO SEAO JULY Cup 2020 ez viewing copy.xlsx')



# # We are dealing with 3 data frame
# # dfa = overall dataframe from filtered data
# # dfb = dataframe that acquired from matches.json. Contains all information about matches and results
# # dfc = dataframe that acquired from teams.json. Contains all information about players, especially teamID and name


dfa = pd.read_excel('Excel_and_CSV/FilteredDecks_Data.xlsx') 
# Add shadowverse class for main data frame
for i in range(1,4):
    dfa[f'class {i}'] = dfa[f'deck {i}'].apply(lambda x: Deck(x).class_checker_svo())

# Obtain matches and removes 'byes' or any invalid matched that doesnt contain statistics data
matchjson = 'https://dtmwra1jsgyb0.cloudfront.net/stages/5f2eb61c0ad5e05d5e217f8c/matches'
response = requests.get(matchjson)        
data = response.json()

dfb = pd.DataFrame(data)
dfb = dfb.fillna(0)
dff = dfb.copy()
dfb = dfb.loc[dfb['stats']!=0].reset_index()

# Obtain teamID and name from json. Then, create a python dictionary based on that.
playerjson = 'https://dtmwra1jsgyb0.cloudfront.net/tournaments/5f0dfe437c4df3491abfc7c2/teams'
response2 = requests.get(playerjson)        
data2 = response2.json()

dfc = pd.DataFrame(data2)
dfc = dfc[['_id', 'name']].rename(columns={'_id':'teamID'})
dfc = dfc.set_index('teamID')
playerdict = dfc.to_dict() 

#Obtain win-loss swiss record from standings
standingsjson = 'https://dtmwra1jsgyb0.cloudfront.net/stages/5f2eb61c0ad5e05d5e217f8c/latest-round-standings'
response3 = requests.get(standingsjson)        
data3 = response3.json()

# add swiss-win-loss into alldf
df1 = pd.DataFrame(data3)
df2 = pd.DataFrame(list(df1['team'])).rename(columns={'_id':'teamID'})
df = df1.merge(df2, on='teamID')
# df = df.loc[(df['wins']>2) & (df['losses']<3) & (df['disqualified']== False)]
df = df[['name', 'wins','losses']]
alldf = dfa.merge(df, on='name')

# Scrap info about Wins, Loss, Bans
alldf = sh.get_ban_data(alldf, dfb, dfc)
alldf = sh.get_win_loss_data(alldf, dfb, dfc, playerdict)

for i in range(1,4):
    alldf[f'deck {i} W/L/B'] = alldf[f'win {i}'].apply(int).apply(str) + '/' + alldf[f'loss {i}'].apply(int).apply(str) + '/' + alldf[f'ban {i}'].apply(int).apply(str)

#export this one for View
alldf_view = alldf[['name', 'wins','deck 1', 'deck 2', 'deck 3', 'deck 1 W/L/B', 'deck 2 W/L/B', 'deck 3 W/L/B']].sort_values(by='wins', ascending=False)
alldf_view = alldf_view.reset_index().drop(['index'], axis=1).set_index(['name'])
#Calculate Win-Ban Archetype Ratio
winbanstats = sh.get_win_ban_archetype(alldf)


writer = pd.ExcelWriter('Excel_and_CSV/Post_SVO_Data.xlsx')
alldf_view.to_excel(writer, 'Sheet1')
winbanstats.to_excel(writer, 'Archetype Stats')
writer.save()

em.excel_convert_quick('Excel_and_CSV/Post_SVO_Data.xlsx')

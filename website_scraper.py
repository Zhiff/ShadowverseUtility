# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 21:29:08 2020
This is website scraper module. Call this from main to extract info from online tournaments, Most json and html handling was done here. more complex thing are moved into stat helper module.

@author: zhafi
"""
import pandas as pd
import requests
import excel_module as em
import stat_helper as sh
import jcg_helper as jcg
from deckmodule import Deck
from bs4 import BeautifulSoup as bs
import numpy as np
import json

#SVO scraper
# This function will create FilteredDecks_View, FilteredDecks_Data, and Statistics for SVO
# Some manual preprocessing is required
# - Decklist sheet name needs to be 'Sheet1' (as specified in convert_quick)
# - Invalid links need to be resolved, otherwise it will return as UNKNOWN UNKNOWN
# - improper svportal links ( most common example is no #lang at the end ) needs to be manually resolved. deckbuilder links is auto-resolved.
def SVO_initial_scraper(svoexcel):
    # Since svo decklist comes in form of excel sheet, no webscraping is required. Simply calls function from excel module
    em.excel_convert_quick(svoexcel, 'Sheet1')
    em.excel_convert_dataset(svoexcel, 3)
    em.excel_statistics('Excel_and_CSV/FilteredDecks_Data.xlsx', 3)
    em.combine_view_and_stats('Excel_and_CSV/FilteredDecks_View.xlsx', 'Names and Links')
    em.add_class_color(3)




#JCG Tourney Link Retriever 
#Retrieves latest tourney of your choosing below:
#1.) pick sv_format = {rotation, unlimited, 2pick}
#2.) tourney_stage = {qualifying, winner}
#3.) check if it's completed (終了)
# Returns the 4 digit string code of the latest tourney for scraping
def JCG_latest_tourney(sv_format, tourney_stage):
    formats = { 'rotation' : 'ローテーション大会' , 'unlimited' : 'アンリミテッド大会' , '2pick' : '2Pick大会' }
    stage = {'group' : 'グループ予選', 'top16' : '決勝トーナメント'}
    
    foundFlag = False
    
    linkschedule = 'https://sv.j-cg.com/schedule/' + sv_format
    source = requests.get(linkschedule).text
    soup = bs(source, 'lxml')
    currentlink = soup.find_all('a', class_='schedule-link')
    
    for link in currentlink:
        jcglink = link.get('href')
        
        c_title = link.find('div', class_='schedule-title').text
        c_hour = link.find('div', class_='schedule-date').text[56:61]
        c_status = link.find('div', class_='schedule-status schedule-status-').text
        
        if (c_status == '開催中') and (stage[tourney_stage] in c_title):
            foundFlag = True
            tcode = jcglink.split('/')[4]
            message = c_title + '\nStatus: Ongoing'
            print(message)
            break
    
    if (foundFlag == False):
        linkpast = 'https://sv.j-cg.com/past-schedule/' + sv_format #1st page or 20 most recent tourney stages
    
        
        source = requests.get(linkpast).text
        soup = bs(source, 'lxml')
        alltlink = soup.find_all('a', class_='schedule-link')
        
        for link in alltlink:
            jcglink = link.get('href')
            
            c_title = link.find('div', class_='schedule-title').text
            c_hour = link.find('div', class_='schedule-date').text[56:61]
            
            if stage[tourney_stage] in c_title:
                tcode = jcglink.split('/')[4]
                message = c_title + '\nStarts: '+ c_hour +' JST (Finished)'
                print(message)
                break
        
    return tcode
    
#JCG scraper
# 1. Retrieve jsonlink and create excel sheet that contains Name, Deck1, and Deck2 (JCG_Raw.xlsx)
# 2. Based on that, it will create FilteredDecks_View, FilteredDecks_Data, and Statistics
# input example 'https://sv.j-cg.com/compe/view/entrylist/2341/json'
def JCG_scraper(tcode, analysis='single'):
    # Grab Json from inside HTML
    jsondf = jcg.grabjsonfromHTML(tcode)
    
    #Filter unnecesarry info and simply create df with name, deck 1, deck 2
    df = jcg.cleanjson(jsondf)
    
    # Additional handling for top16 JCG Data, it will retrieve the ranking and sort it accordingly instead of registration based.
    # if jcg.isTop16JCG(df, tcode):
    if(jcg.isTournamentOver(tcode,'top16')):
        bracketid = jcg.bracketidfinder(tcode)
        namedf = jcg.retrieveTop16JCG(bracketid, tcode)
        data = namedf.merge(df)
        rankings = pd.DataFrame({'Rank':['1st','2nd','3rd/4th','3rd/4th','5th-8th','5th-8th','5th-8th','5th-8th','9th-16th','9th-16th','9th-16th','9th-16th','9th-16th','9th-16th','9th-16th','9th-16th']})
        df = pd.concat([rankings, data],axis=1)
        df = df.dropna()
        df = df[['Rank', 'name', 'deck 1', 'deck 2']]
        
    writer = pd.ExcelWriter('Excel_and_CSV/JCG_Raw.xlsx')
    df.to_excel(writer, index=False)
    writer.save()
    
    if (analysis == 'single'):
        # Calls functions from excel module to process raw sheets
        em.excel_convert_quick('Excel_and_CSV/JCG_Raw.xlsx', 'Sheet1')
        em.excel_convert_dataset('Excel_and_CSV/JCG_Raw.xlsx', 2)
        em.excel_statistics('Excel_and_CSV/FilteredDecks_Data.xlsx', 2)        
        em.combine_view_and_stats('Excel_and_CSV/FilteredDecks_View.xlsx', 'Names and Links')
        
        if(jcg.isTournamentOver(tcode, 'group')):
            top16 = jcg.group_winner_check(tcode)
            em.add_top16_names(top16)
            em.add_conversion_rate(top16)   
            em.add_class_color(1)
        else:
            em.add_class_color(3)
            
    elif (analysis == 'multiple'):
        em.excel_convert_dataset('Excel_and_CSV/JCG_Raw.xlsx', 2)
        df = em.count_deck('Excel_and_CSV/FilteredDecks_Data.xlsx', 2)
        
    
    return df
        

        
#Scrap data from MS Gaming in Battlefy
#requirements : Json link : //tournaments/..../teams . Can be found in response at Participants tab
#input example https://dtmwra1jsgyb0.cloudfront.net/tournaments/5f1e79da534e897bd0c64673/teams 
def manasurge_bfy_scraper(jsonlink):
    response = requests.get(jsonlink)        
    data = response.json()
    
    # Grab Dataframe, decklist were located in another dictionary inside customFields
    # expand Customfields by temp df, then merge them to orginal df
    df1 = pd.DataFrame(data)
    df2 = pd.DataFrame(list(df1['customFields']))
    df2['name'] = df1['name']
    df = df1.merge(df2)
    
    # Decklist were in column 2 , 3 , and 4 (Different tournament may use different fields)
    # Decklist were inside another dictionary. Use nested for loop to obtain actual decklist and update our df
    df = df[['name',2,3,4]]
    total_participants = df.shape[0] 
    for i in range(2,5):
        for j in range(0,total_participants):
            df[i][j] = df[i][j]['value']
    
    df = df.rename(columns={2:'deck 1', 3:'deck 2', 4:'deck 3'})
    df = sh.handle_duplicate_row(df, 'name')
    
    writer = pd.ExcelWriter('Excel_and_CSV/MS_Raw.xlsx')
    df.to_excel(writer)
    writer.save()
    
    # Calls functions from excel module to process raw sheets
    em.excel_convert_quick('Excel_and_CSV/MS_Raw.xlsx', 'Sheet1')
    em.excel_convert_dataset('Excel_and_CSV/MS_Raw.xlsx', 3)
    em.excel_statistics('Excel_and_CSV/FilteredDecks_Data.xlsx', 3)
    em.combine_view_and_stats('Excel_and_CSV/FilteredDecks_View.xlsx', 'Names and Links')
    em.add_class_color(3)
    
# Scrap info from battlefy to see W/L/B stats and Archetype stats in Post_SVO file.
# Prerequisite : SVO_initial_scraper must be run first. FilteredDecks_Data should contain all participants
# Input : battlefy tourneyhash and stagehash
# example : https://battlefy.com/shadowverse-open/svo-seao-monthly-cup-september/5f02c8825522b86652930ae3/stage/5f6574dd1104cd7a261297b9/bracket/7
# 5f02c8825522b86652930ae3 is tourney hash and 5f6574dd1104cd7a261297b9 is stagehash
def SVO_posttourney_scraper(tourneyhash , stagehash):
    # # We are dealing with 3 data frame
    # # dfa = overall dataframe from filtered data
    # # dfb = dataframe that acquired from matches.json. Contains all information about matches and results
    # # dfc = dataframe that acquired from teams.json. Contains all information about players, especially teamID and name
    

    dfa = pd.read_excel('Excel_and_CSV/FilteredDecks_Data.xlsx') 
    
    # Obtain matches and removes 'byes' or any invalid matched that doesnt contain statistics data
    matchjson = 'https://dtmwra1jsgyb0.cloudfront.net/stages/'+ stagehash + '/matches'
    response = requests.get(matchjson)        
    data = response.json()
    
    dfb = pd.DataFrame(data)
    dfb = dfb.fillna(0)
    dfb = dfb.loc[dfb['stats']!=0].reset_index()
    
    # Obtain teamID and name from json. Then, create a python dictionary based on that.
    playerjson = 'https://dtmwra1jsgyb0.cloudfront.net/tournaments/' + tourneyhash + '/teams'
    response2 = requests.get(playerjson)        
    data2 = response2.json()
    
    dfc = pd.DataFrame(data2)
    dfc = dfc[['_id', 'name']].rename(columns={'_id':'teamID'})
    dfc = dfc.set_index('teamID')
    playerdict = dfc.to_dict() 
    
    #Obtain win-loss swiss record from standings
    standingsjson = 'https://dtmwra1jsgyb0.cloudfront.net/stages/' + stagehash + '/latest-round-standings'
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
    
    # Create string for that contains W / L / B
    for i in range(1,4):
        alldf[f'deck {i} W/L/B'] = alldf[f'win {i}'].apply(int).apply(str) + '/' + alldf[f'loss {i}'].apply(int).apply(str) + '/' + alldf[f'ban {i}'].apply(int).apply(str)
    
    #export cleaned data for View
    alldf_view = alldf[['name', 'wins','deck 1', 'deck 2', 'deck 3', 'deck 1 W/L/B', 'deck 2 W/L/B', 'deck 3 W/L/B']].sort_values(by='wins', ascending=False)
    alldf_view = alldf_view.reset_index().drop(['index'], axis=1).set_index(['name'])
    
    #Calculate Win-Ban Archetype Ratio
    winbanstats = sh.get_win_ban_archetype(alldf)
    
    writer = pd.ExcelWriter('Excel_and_CSV/Post_SVO_Data.xlsx',options={'strings_to_urls': False})
    alldf_view.to_excel(writer, 'Names and Links')
    winbanstats.to_excel(writer, 'Archetype Stats')
    writer.save()
    
    # convert svoportal link to archetype name
    em.excel_convert_quick('Excel_and_CSV/Post_SVO_Data.xlsx', 'Names and Links', True)
    em.add_class_color(2)

    
# This function will retrieve matches and bans for queried player. It will return a dataframe that can be observed in Main file.
# Sample input :
# player = 'TK Zy'
# tourneyhash = '5f02c761bf38ff0aa1f90bcf'
# stagehash = '5f37504d6ce6de28d63dd645'
def SVO_ban_peek(player, tourneyhash, stagehash):
    
    dfa = pd.read_excel('Excel_and_CSV/FilteredDecks_Data.xlsx') 
        
    # Obtain matches and removes 'byes' or any invalid matched that doesnt contain statistics data
    matchjson = 'https://dtmwra1jsgyb0.cloudfront.net/stages/'+ stagehash + '/matches'
    response = requests.get(matchjson)        
    data = response.json()
    
    dfb = pd.DataFrame(data)
    dfb = dfb.fillna(0)
    dfb = dfb.loc[dfb['stats']!=0].reset_index()
    
    # Obtain teamID and name from json. Then, create a python dictionary based on that.
    playerjson = 'https://dtmwra1jsgyb0.cloudfront.net/tournaments/' + tourneyhash + '/teams'
    response2 = requests.get(playerjson)        
    data2 = response2.json()
    
    dfc = pd.DataFrame(data2)
    dfc = dfc[['_id', 'name']].rename(columns={'_id':'teamID'})
    dfc = dfc.set_index('teamID')
    playerdict = dfc.to_dict() 
    
    dfb['top teamID'] = dfb.loc[:,'top'].apply(lambda x: x['teamID'])
    dfb['bot teamID'] = dfb.loc[:,'bottom'].apply(lambda x: x['teamID'])
    dfb['player 1'] = dfb.loc[:,'top teamID'].apply(lambda x: playerdict['name'][x])
    dfb['player 2'] = dfb.loc[:,'bot teamID'].apply(lambda x: playerdict['name'][x])
    dfb['player 1 banned'] = dfb.loc[:,'top'].apply(lambda x: x.get('bannedClass', 'none') )
    dfb['player 2 banned'] = dfb.loc[:,'bottom'].apply(lambda x: x.get('bannedClass', 'none'))
    
    # Quick Class View
    dfview = dfb.copy()
    dfview = dfview[['player 1', 'player 1 banned', 'player 2 banned', 'player 2']]
    
    dictionary = dfa[['name','class 1','class 2','class 3','arc 1','arc 2','arc 3']].copy()
    dictionary.astype({'name':'str'})
    for i in range (1,4):
        dictionary[f'nameclass{i}'] = dictionary['name'] + dictionary[f'class {i}']
        
    nameclass = dictionary.loc[:,'nameclass1':'nameclass3'].stack().reset_index().rename(columns={0:'nameclass'})
    arche = dictionary.loc[:,'arc 1':'arc 3'].stack().reset_index().rename(columns={0:'archetype'})
    diction = pd.concat([nameclass, arche], axis=1)
    diction = diction[['nameclass','archetype']].set_index('nameclass')
    pa_dict = diction.to_dict()
    
    dffinal = dfview.copy()
    dffinal['playerarc1'] = dffinal['player 1']+ dffinal['player 1 banned']
    dffinal['playerarc2'] = dffinal['player 2']+ dffinal['player 2 banned']
    dffinal['Banned 1'] = dffinal.loc[:,'playerarc1'].apply(lambda x: pa_dict.get('archetype').get(x, 'Unknown Unknown'))
    dffinal['Banned 2'] = dffinal.loc[:,'playerarc2'].apply(lambda x: pa_dict.get('archetype').get(x, 'Unknown Unknown'))
    
    dffinal = dffinal[['player 1', 'Banned 1', 'Banned 2', 'player 2']]
    
    search = dffinal[(dffinal['player 1']==f'{player}') | (dffinal['player 2']==f'{player}')]
    
    return search

# standingsjson = 'https://dtmwra1jsgyb0.cloudfront.net/stages/5f8b0e98c7530d53c082744c/latest-round-standings'
# response = requests.get(standingsjson)        
# data = response.json()

# df1 = pd.DataFrame(data)
# df2 = pd.DataFrame(list(df1['team'])).rename(columns={'_id':'teamID'})
# df3 = df2[['name','countryFlag']]
# df4 = df3.iloc[0:32]

# dfa = pd.read_excel('Excel_and_CSV/Tempostorm.xlsx')
# dfb = df4.merge(dfa)

# writer = pd.ExcelWriter("Excel_and_CSV/TSTop32.xlsx")
# dfb.to_excel(writer, 'Top32')
# writer.save()

# # Input : JCG competition ID lists

# jcgid = ['2399','2419','2422', '2425', '2426', '2428', '2431', '2433', '2436', '2440', '2466', '2468', '2471', '2472', '2474','2477','2480','2482', '2504', '2505'] #group

def generate_archetype_trends(jcgIDs):
    flag_first = True
    for ids in jcgIDs:
        # Find the Date
        link = 'https://sv.j-cg.com/compe/' + ids
        source = requests.get(link).text
        soup = bs(source, 'lxml')
        date = soup.find_all('span', class_='nobr')[6].text
        # Find the Json
        # json = 'https://sv.j-cg.com/compe/view/entrylist/'+ ids + '/json'
        decks = JCG_scraper(ids, 'multiple')
        
        if decks is not None: #Validity Check
            if flag_first == True:
                #For the first instance, we simply initialize the data frame
                arc_df = decks.rename(columns={'Count':date})
                flag_first = False
            else:
                #Append dataframe with new dataframe
                added_df = decks.rename(columns={'Count':date})
                arc_df = pd.merge(arc_df, added_df, on='Deck Archetype', how='outer')
                
    arc_df = arc_df.fillna(0)
    writer = pd.ExcelWriter("Excel_and_CSV/Graph.xlsx")
    arc_df.to_excel(writer, 'stats', index=False)
    writer.save()


#DSAL
def DSAL_scraper(link):
    link = 'http://www.littleworld.tokyo/RoundOfDarkness/openingPartySecond'
    source = requests.get(link).text
    soup = bs(source, 'lxml')
    # Team Scraper
    teamcontainer = soup.find_all('div', class_='pricing')
    teamlist = []
    for team in teamcontainer:
        teamname = team.find('h1').text
        teamlist.append(teamname)
        
    # Deck Scraper
    deckcontainer = soup.find_all('button', class_='btn btn-round btn-info')
    deck1list = []
    deck2list = []
    deck3list = []
    deck4list = []
    deck5list = []
    
    for links in deckcontainer[::5]:
        ocdeck = links.get('onclick')
        deck = ocdeck.split("'")[1]
        deck1list.append(deck)
    for links in deckcontainer[1::5]:
        ocdeck = links.get('onclick')
        deck = ocdeck.split("'")[1]
        deck2list.append(deck)
    for links in deckcontainer[2::5]:
        ocdeck = links.get('onclick')
        deck = ocdeck.split("'")[1]
        deck3list.append(deck)
    for links in deckcontainer[3::5]:
        ocdeck = links.get('onclick')
        deck = ocdeck.split("'")[1]
        deck4list.append(deck)
    for links in deckcontainer[4::5]:
        ocdeck = links.get('onclick')
        deck = ocdeck.split("'")[1]
        deck5list.append(deck)
    # Combine everything and rename
    db = np.column_stack((teamlist, deck1list, deck2list, deck3list, deck4list, deck5list))
    df = pd.DataFrame(db)
    df = df.rename(columns={0:'name', 1:'deck 1', 2:'deck 2', 3:'deck 3', 4:'deck 4', 5:'deck 5'})
    
    writer = pd.ExcelWriter('Excel_and_CSV/DSAL_Raw.xlsx')
    df.to_excel(writer, index=False) 
    writer.save()
    
    em.excel_convert_quick('Excel_and_CSV/DSAL_Raw.xlsx', 'Sheet1')
    em.excel_convert_dataset('Excel_and_CSV/DSAL_Raw.xlsx', 5)
    em.excel_statistics('Excel_and_CSV/FilteredDecks_Data.xlsx', 5)
    em.combine_view_and_stats('Excel_and_CSV/FilteredDecks_View.xlsx', 'Names and Links')
    em.add_class_color(3)

#new BFY
# tourneyhash = '5fe551f5726d0b11ab383a6e'
# stagehash = '6002492e7c4ead11982f6c9a'

# teamjson = 'https://dtmwra1jsgyb0.cloudfront.net/tournaments/'+ tourneyhash + '/teams'
# response = requests.get(teamjson)        
# data = response.json()
# dfa = pd.DataFrame(data)

# participantsjson = 'https://dtmwra1jsgyb0.cloudfront.net/tournaments/'+ tourneyhash + '/participants'
# response = requests.get(participantsjson)        
# data = response.json()
# dfb = pd.DataFrame(data)

# standingsjson = 'https://dtmwra1jsgyb0.cloudfront.net/stages/'+ stagehash + '/latest-round-standings'
# response = requests.get(standingsjson)        
# data = response.json()
# dfc = pd.DataFrame(data)

# statsjson = 'https://dtmwra1jsgyb0.cloudfront.net/stages/'+ stagehash + '/stats'
# response = requests.get(statsjson)        
# data = response.json()
# dfd = pd.DataFrame(data)

# matchjson = 'https://dtmwra1jsgyb0.cloudfront.net/stages/'+ stagehash + '/matches'
# response = requests.get(matchjson)        
# data = response.json()
# dfe = pd.DataFrame(data)






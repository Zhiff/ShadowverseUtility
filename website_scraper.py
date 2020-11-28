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
from deckmodule import Deck
from bs4 import BeautifulSoup as bs
import numpy as np


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
    em.add_class_color(1)




#JCG Tourney Link Retriever 
#Retrieves latest tourney of your choosing below:
#1.) pick sv_format = {rotation, unlimited, 2pick}
#2.) tourney_stage = {qualifying, winner}
#3.) check if it's completed (終了)
# Returns the 4 digit string code of the latest tourney for scraping
def JCG_latest_tourney(sv_format, tourney_stage):

    jcglink = 'https://sv.j-cg.com/compe/' + sv_format #1st page or 20 most recent tourney stages
    formats = { 'rotation' : 'ローテーション大会' , 'unlimited' : 'アンリミテッド大会' , '2pick' : '2Pick大会' }
    stage = {'group' : 'グループ予選', 'top16' : '決勝トーナメント'}
    
    source = requests.get(jcglink).text
    soup = bs(source, 'lxml')
    
    ongoing = soup.find_all('tr', class_="competition")
    # finished = soup.find_all('tr', class_="competition commit") #tourney strted/finish while class_="competition" -> tourney has not started 
    # tourney = ongoing + finished
    latest_tourney = False
     
    #Find relevant data in 'tourney' need (dates are also found in 'tourney')
    for tourney_code in ongoing:
        name_text = tourney_code.find_all('span', class_="nobr")   
        potential_format = name_text[-2].text
        potential_stage = name_text[-1].text
        potential_status = tourney_code.find('td', class_="status").text
        
        #Does it meet our conditions? (Note: First one is always the latest so no dates were used for now)
        if potential_format == formats[sv_format] and potential_stage == stage[tourney_stage] and potential_status == '開催中':
            latest_tourney = True
            potential_id = tourney_code.get("competition_id")
            latest_tourney_code = str(potential_id)
            tourney_date = tourney_code.find('td', class_="date").text + '(Still Ongoing)'
            break
        elif potential_format == formats[sv_format] and potential_stage == stage[tourney_stage] and potential_status == '終了':
            latest_tourney = True
            potential_id = tourney_code.get("competition_id")
            latest_tourney_code = str(potential_id)
            tourney_date = tourney_code.find('td', class_="date").text + '(Finished)'
            break
    
    if latest_tourney:
        print(f'Tournament Date: {tourney_date}')
    if latest_tourney == False:
        latest_tourney_code = None
    
    return latest_tourney_code     
    
#JCG scraper
# 1. Retrieve jsonlink and create excel sheet that contains Name, Deck1, and Deck2 (JCG_Raw.xlsx)
# 2. Based on that, it will create FilteredDecks_View, FilteredDecks_Data, and Statistics
# input example 'https://sv.j-cg.com/compe/view/entrylist/2341/json'
def JCG_scraper(tcode, analysis='single'):
    jsonlink = 'https://sv.j-cg.com/compe/view/entrylist/' + tcode + '/json'
    jcglink = jsonlink
    response = requests.get(jcglink)
    data1 = response.json()
    data2 = pd.DataFrame(list(data1['participants']))
    data3 = data2.loc[data2['te'] == 1] # Only filter those who checked in
    data4 = pd.DataFrame(list(data3['dk'])).rename(columns={0:'deck 1',1:'deck 2'}) #Grab df from column dk, then rename it properly
    data5 = data3['nm'].reset_index().drop(['index'], axis=1) #create a series with name only
    data6 = pd.concat([data5, data4], axis=1) #combine name and deck1,deck2
    
    #JCG deck syntax Handling
    sv = 'https://shadowverse-portal.com/deck/'
    lang_eng = '?lang=en'
    data6 = data6.rename(columns={'nm':'name'})
    data6['deck 1'] = data6['deck 1'].apply(lambda x: x['hs'] if x else None)
    data6['deck 1'] = data6['deck 1'].apply(lambda x: sv + x + lang_eng if x else 'Invalid Deck')
    data6['deck 2'] = data6['deck 2'].apply(lambda x: x['hs'] if x else '')
    data6['deck 2'] = data6['deck 2'].apply(lambda x: sv + x + lang_eng if x else 'Invalid Deck')
    
    data7 = sh.handle_duplicate_row(data6, 'name')
    df = data7
    
    # Additional handling for top16 JCG Data, it will retrieve the ranking and sort it accordingly instead of registration based.
    if sh.isTop16JCG(data6, jsonlink):
        namedf = sh.retrieveTop16JCG(jsonlink)
        data8 = namedf.merge(data7)
        rankings = pd.DataFrame({'Rank':['1st','2nd','3rd/4th','3rd/4th','5th-8th','5th-8th','5th-8th','5th-8th','9th-16th','9th-16th','9th-16th','9th-16th','9th-16th','9th-16th','9th-16th','9th-16th']})
        df = pd.concat([rankings, data8],axis=1)
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
        
        if (sh.IsGroupStageOver(tcode)):
            tour = 'https://sv.j-cg.com/compe/view/tour/' + tcode
            top16 = JCG_group_winner_check(tour)
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
    em.add_class_color(1)
    
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

def JCG_group_winner_check(url):
    source = requests.get(url).text
    soup = bs(source, 'lxml')
    
    names = []
    deck1 = []
    deck2 = []
    
    allfinal = soup.find_all('div', class_='round round4')
    
    for finalround in allfinal:
        
        fin = finalround.select('li')[1]
        right = fin.find('li', class_='tour_match right winner')
        left = fin.find('li', class_='tour_match left winner')    
        finalpage = str(fin).split("'")[1]
        urllink = finalpage
        
        match = requests.get(urllink).text
        soupm = bs(match, 'lxml') 
        
        if left: 
            name = left.find('div').text
            links = soupm.find('div', class_='team_wrap leftteam').find_all('a')
        elif right:
            name = right.find('div').text
            links = soupm.find('div', class_='team_wrap rightteam').find_all('a')
        else:
            name = 'N/A'
            links = 'N/A'
            arc1 = 'N/A'
            arc2 = 'N/A'
        
        if links != 'N/A':
            decka = links[0].get('href')
            arc1 =  Deck(decka).archetype_checker()
            deckb = links[1].get('href')
            arc2 =  Deck(deckb).archetype_checker()
        
        names.append(name)
        deck1.append(arc1)
        deck2.append(arc2) 
    
    df = pd.DataFrame([names,deck1,deck2]).transpose().rename(columns={0:'name', 1:'arc 1', 2:'arc 2'})
    return df




# Incomplete code for JCG archetype winrate calculator.

# df = pd.read_excel('Excel_and_CSV/FilteredDecks_Data.xlsx')
# df = df[['name','arc 1', 'arc 2']]

# url = 'https://sv.j-cg.com/compe/view/tour/2334'
# source = requests.get(url).text
# soup = bs(source, 'lxml')

# winnerlist = []
# winleft = soup.find_all('li', class_="tour_match left winner")

# for win in winleft:
#     name = win.findNext().findNext().text
#     winnerlist.append(name)

# winright = soup.find_all('li', class_="tour_match right winner")
# for win in winright:
#     name = win.findNext().findNext().text
#     winnerlist.append(name)

# windf = pd.DataFrame(winnerlist).rename(columns={0:'name'})

# loserlist = []
# loseleft = soup.find_all('li', class_="tour_match left")
# for lose in loseleft:
#     name = lose.findNext().findNext().text
#     loserlist.append(name)
    
# loseright = soup.find_all('li', class_="tour_match right")
# for lose in loseright:
#     name = lose.findNext().findNext().text
#     loserlist.append(name)

# lossdf = pd.DataFrame(loserlist).rename(columns={0:'name'})

# win = df.merge(windf, how='inner', on='name')
# wintotal = win.loc[:,'arc 1':'arc 2'].stack().value_counts(normalize = False, ascending = False)
# wintotal = wintotal.rename_axis("Deck Archetype").reset_index(name = 'WinTotal')


# loss = df.merge(lossdf, how='inner', on='name')
# losstotal = loss.loc[:,'arc 1':'arc 2'].stack().value_counts(normalize = False, ascending = False)
# losstotal = losstotal.rename_axis("Deck Archetype").reset_index(name = 'LossTotal')

# summary = wintotal[['Deck Archetype','WinTotal']]
# summary['LossTotal'] = losstotal['LossTotal']
# summary['Winrate'] = summary['WinTotal']/(summary['WinTotal'] + summary['LossTotal'])
    
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

# jcgid = ['2399','2419','2422', '2425', '2426', '2428', '2431', '2433', '2436'] #group
# jcgid = ['2418', '2442', '2445', '2448', '2449', '2451', '2454', '2456', '2460'] #top16
def generate_archetype_trends(jcgIDs):
    flag_first = True
    for ids in jcgIDs:
        # Find the Date
        link = 'https://sv.j-cg.com/compe/' + ids
        source = requests.get(link).text
        soup = bs(source, 'lxml')
        date = soup.find_all('span', class_='nobr')[6].text
        # Find the Json
        json = 'https://sv.j-cg.com/compe/view/entrylist/'+ ids + '/json'
        decks = JCG_scraper(json, 'multiple')
        
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
    em.add_class_color(1)
    
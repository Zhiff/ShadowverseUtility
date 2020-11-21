# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:19:41 2020
This is statistics helper module. Functions in this module will help to take care all the stuffs that needed 
to create clean excel/df based statistics. mostly being called by excel_module
@author: zhiff
"""

import pandas as pd
from bs4 import BeautifulSoup as bs
import requests

def add_lineup_column_3decks(df):
    # add new column which contains all 3 decks, then make them as Set to take care the uniformity
    df_added_lineup = df.assign(Lineup = list(zip(df['arc 1'],df['arc 2'],df['arc 3'])) )
    df_added_lineup['Lineup'] = df_added_lineup['Lineup'].apply(set)
    return df_added_lineup

def add_lineup_column_2decks(df):
    # add new column which contains all 2 decks, then make them as Set to take care the uniformity
    df_added_lineup = df.assign(Lineup = list(zip(df['arc 1'],df['arc 2'])) )
    df_added_lineup['Lineup'] = df_added_lineup['Lineup'].apply(set)
    return df_added_lineup

def add_lineup_column_5decks(df):
    # add new column which contains all 2 decks, then make them as Set to take care the uniformity
    df_added_lineup = df.assign(Lineup = list(zip(df['arc 1'],df['arc 2'],df['arc 3'],df['arc 4'],df['arc 5'])) )
    df_added_lineup['Lineup'] = df_added_lineup['Lineup'].apply(set)
    return df_added_lineup


def get_lineup_df(df):
    # creating a new df that consists of lineup and the number of people that bringing that lineup in tourney
    lineup = df["Lineup"].value_counts(normalize = False, ascending = False)
    lineup = lineup.rename_axis("Lineup").reset_index(name = 'Count')
    lineup['Player %'] = (round((lineup['Count']/(int(df.shape[0])))*100, 2))
    return lineup

def get_decks_df(df, maxdeck):
    # creating a new df that consists of archetypes and the number of people that bringing that archetype in tourney
    decks = df.loc[:,'arc 1':f'arc {maxdeck}'].stack().value_counts(normalize = False, ascending = False)
    decks = decks.rename_axis("Deck Archetype").reset_index(name = 'Count')
    decks['Player %'] = (round((decks['Count']/(int(df.shape[0])))*100, 2))
    return decks

def add_statistics_tool(df):
    # count average, median, and standard Deviation and add them into df
    mean = round(df.mean(axis=1),2)
    median = df.median(axis=1)
    std = round(df.std(axis=1),2)
    # if there is more than 3 players, add card copies details as info
    if (len(df.columns)>3):
        count = df.apply(lambda x:x.value_counts(normalize=True), axis=1).fillna(0)
        df = pd.concat([df,count], axis=1)
    df['Median'] = median
    df['Std Deviation'] = std
    df['Average'] = mean
    return df


#filter for popular archetype, nowadays i just keep it as 1 as min occurence because we want to see the whole thing
def get_popular_archetype(df, min_occurrence, maxdeck):
        
    # check the number of occurence (refer to statistics)
    decks =  get_decks_df(df, maxdeck)
    decks = decks.loc[decks['Count'] >= min_occurrence]
    popular_archetype = decks['Deck Archetype'].tolist()
    return popular_archetype

# This function will add ban 1, ban 2, ban 3, and total ban into master dataframe. required for W/L/B data
def get_ban_data(dfa, dfb, dfc):
    # Create a dataframe that contains 'name' and 'bannedClass'(dfd) by merging data from matches (dfb) and teams (dfc)
    dfb1 = pd.DataFrame(list(dfb['top']))
    dfb1a = pd.merge(dfb1, dfc, on='teamID')
    dfb2 = pd.DataFrame(list(dfb['bottom']))
    dfb2a = pd.merge(dfb2, dfc, on='teamID')
    dfd = pd.concat([dfb1a, dfb2a]).reset_index()
    
    #add count, than we sum the values using groupby of name. So in the end we get df that consists of name : bannedClass : count
    dfd['count'] = 1
    dfd1 = dfd[['teamID', 'name', 'bannedClass','winner','score','disqualified','count']]
    dfd2 = dfd1.groupby(['name','bannedClass']).count().reset_index() 
    dfd3 = dfd2[['name','bannedClass','count']] # Clean dataset of name, banned, count
    
    # merge filtered DF to master DF
    dfa = dfa.rename(columns={'class 1':'bannedClass'})
    dfd3a = pd.merge(dfa, dfd3, how='left')
    dfd3a = dfd3a.rename(columns={'bannedClass':'class 1','class 2':'bannedClass','count':'ban 1'})
    dfd3b = pd.merge(dfd3a, dfd3, how='left')
    dfd3b = dfd3b.rename(columns={'bannedClass':'class 2','class 3':'bannedClass','count':'ban 2'})
    dfd3c = pd.merge(dfd3b, dfd3, how='left')
    dfd3c = dfd3c.rename(columns={'bannedClass':'class 3','count':'ban 3'})
    dfd3c = dfd3c.fillna(0)
    
    # Caluclate ban percentage
    dfd3c['totalban'] = dfd3c['ban 1'] + dfd3c['ban 2'] + dfd3c['ban 3']
    for i in range(1,4):
            dfd3c[f'ban {i} rate'] = round(dfd3c[f'ban {i}']/ dfd3c['totalban'], 2)
    
    dfd3c = dfd3c.fillna(0)
    return dfd3c

# This function will add win 1, win 2, win 3, loss 1, loss 2, loss 3 and total match into master dataframe. required for W/L/B data
def get_win_loss_data(dfa, dfb, dfc, playerdict):
    # create a new column, called top name and bot name. first, retrieve team ID from top, then convert team ID into actual name based on playerdict 
    dfb['top teamID'] = dfb.loc[:,'top'].apply(lambda x: x['teamID'])
    dfb['bot teamID'] = dfb.loc[:,'bottom'].apply(lambda x: x['teamID'])
    dfb['top name'] = dfb.loc[:,'top teamID'].apply(lambda x: playerdict['name'][x])
    dfb['bot name'] = dfb.loc[:,'bot teamID'].apply(lambda x: playerdict['name'][x])
    
    # Keep traversing inside the json until we arrived to our desired contents. these specific operations are required due to complexity of BFY JSON
    dfb1 = pd.DataFrame(list(dfb['stats'])) 
    dfb2 = dfb1.loc[:,0:2].stack().reset_index()
    dfb3 = pd.DataFrame(list(dfb2[0]))
    dfb = dfb.rename(columns={'_id':'matchID'})
    dfb3a = pd.merge(dfb3, dfb, on='matchID')
    dfb4 = pd.DataFrame(list(dfb3['stats'])) 
    # based on dfb, there are 2 locations for match stats, keep traversing
    dfb4top = pd.DataFrame(list(dfb4['top']))
    dfb4top['name'] = dfb3a['top name'] 
    dfb4bot = pd.DataFrame(list(dfb4['bottom']))
    dfb4bot['name'] = dfb3a['bot name'] 
    
    # Combine both top and bottom, so we have complete picture, then count it
    allmatch = pd.concat([dfb4top,dfb4bot]) 
    allmatch['count'] = 1
    allmatch1 = allmatch.groupby(['name','class','winner']).count().reset_index()
    allmatch2 = allmatch1[['name','class','winner','count']]
    
    # Separate Win and Lose data
    dfwin = allmatch2.loc[allmatch2['winner'] == True].drop(['winner'], axis=1)
    dfloss = allmatch2.loc[allmatch2['winner'] == False].drop(['winner'], axis=1)
    
    # merge filtered win DF into master DF
    dfa = dfa.rename(columns={'class 1':'class'})
    dfd3a = pd.merge(dfa, dfwin, how='left')
    dfd3a = dfd3a.rename(columns={'class':'class 1','class 2':'class','count':'win 1'})
    dfd3b = pd.merge(dfd3a, dfwin, how='left')
    dfd3b = dfd3b.rename(columns={'class':'class 2','class 3':'class','count':'win 2'})
    dfd3c = pd.merge(dfd3b, dfwin, how='left')
    dfd3c = dfd3c.rename(columns={'class':'class 3','count':'win 3'})
    dfd3c = dfd3c.fillna(0)
    
    # merge filtered loss DF into master DF
    dfd3c = dfd3c.rename(columns={'class 1':'class'})
    dfd3d = pd.merge(dfd3c, dfloss, how='left')
    dfd3d = dfd3d.rename(columns={'class':'class 1','class 2':'class','count':'loss 1'})
    dfd3e = pd.merge(dfd3d, dfloss, how='left')
    dfd3e = dfd3e.rename(columns={'class':'class 2','class 3':'class','count':'loss 2'})
    dfd3f = pd.merge(dfd3e, dfloss, how='left')
    dfd3f = dfd3f.rename(columns={'class':'class 3','count':'loss 3'})
    dfd3f = dfd3f.fillna(0)
    
    # Calculate percentage
    for i in range(1,4):
        dfd3f[f'total match {i}'] = dfd3f[f'win {i}'] + dfd3f[f'loss {i}']
        dfd3f[f'win {i} rate'] = round(dfd3f[f'win {i}']/ dfd3f[f'total match {i}'], 2)
    
    dfd3f = dfd3f.fillna(0)    
    return dfd3f

# This function is respinsible for creating a dataframe for win ban percentage for all archetype. It will be featured in Archetype Stats sheet in post svo result.
def get_win_ban_archetype(alldf):
    # Make a df that only consists of archetypes, and their ban percentage for every single player
    decks = alldf.loc[:,'arc 1':'arc 3'].stack().reset_index().rename(columns={0:'archetype'})
    bans = alldf.loc[:,'ban 1 rate':'ban 3 rate'].stack().reset_index().rename(columns={0:'ban percentage'})
    db = pd.concat([decks, bans], axis=1)[['archetype', 'ban percentage']]
    
    # Archetype ban percentage = average of all ban percentage received by each player
    db = db.groupby('archetype').mean()
    db['ban percentage'] = round(db['ban percentage'], 4)
    
    # Make a df that consists archetype, win total, and match total
    wins = alldf.loc[:,'win 1':'win 3'].stack().reset_index().rename(columns={0:'win total'})
    matches =  alldf.loc[:,['total match 1','total match 2','total match 3']].stack().reset_index().rename(columns={0:'match total'})
    wr = pd.concat([decks, wins, matches], axis=1)[['archetype','win total','match total']]
    
    # Archetype win percentage = total win / total match
    wr = wr.groupby('archetype').sum()
    wr['win percentage']= round(wr['win total']/wr['match total'], 4)
    
    # concat both winrate and banrate
    winbanstats = pd.concat([wr,db], axis=1)
    winbanstats = winbanstats.fillna(0)
    
    return winbanstats

def isTop16JCG(df, jsonlink):
    top16JCG = False
    if (len(df.index) <= 16):
        compeID = jsonlink.split('/')[6]
        homepage = 'https://sv.j-cg.com/compe/' + compeID
        source = requests.get(homepage).text
        soup = bs(source, 'lxml')
        placement = soup.find('p', class_="rank rank-1")
        if (placement != None):
            top16JCG = True
            
    return top16JCG

def retrieveTop16JCG(jsonlink):
    compeID = jsonlink.split('/')[6]
    tourpage = 'https://sv.j-cg.com/compe/view/tour/' + compeID
    source = requests.get(tourpage).text
    soup = bs(source, 'lxml')
    
    namelist = []
    legend = soup.find_all('div', class_='name_abbr')
    for entry in legend:
        namelist.append(entry.text)
    
    namedf = pd.DataFrame(namelist).rename(columns={0:'name'})
    namedf = namedf['name'].value_counts().rename_axis("name").reset_index(name = 'Count')
    
    mainpage = 'https://sv.j-cg.com/compe/' + compeID
    source2 = requests.get(mainpage).text
    soup2 = bs(source2, 'lxml')
    
    firstplace = soup2.find('p', class_='rank rank-1').findNext().text
    secondplace = soup2.find('p', class_='rank rank-2').findNext().text
    
    namedf.at[0,'name'] = firstplace
    namedf.at[1,'name'] = secondplace
    
    return namedf

def deck_quick_count(df):
    decks = df.loc[:,'deck 1':'deck 2'].stack().value_counts(normalize = False, ascending = False)
    decks = decks.rename_axis("Deck Archetype").reset_index(name = 'Count')
    
    return decks

def handle_duplicate_row(df, columnname):    
    df[columnname] = df[columnname].where(~df[columnname].duplicated(), df[columnname] + '_dp')
    df[columnname] = df[columnname] + df.groupby(by=columnname).cumcount().astype(str).replace('0','')
    return df

# # incomplete code for Archetype Matchup. Abandoned due to low sample in single SVO which makes the data kinda nonsense. Might be revisited if somehow SVO becomes bigger 
    
# dfb['top teamID'] = dfb.loc[:,'top'].apply(lambda x: x['teamID'])
# dfb['bot teamID'] = dfb.loc[:,'bottom'].apply(lambda x: x['teamID'])
# dfb['player 1'] = dfb.loc[:,'top teamID'].apply(lambda x: playerdict['name'][x])
# dfb['player 2'] = dfb.loc[:,'bot teamID'].apply(lambda x: playerdict['name'][x])
    
# # Keep traversing inside the json until we arrived to our desired contents. these specific operations are required due to complexity of BFY JSON
# dfb1 = pd.DataFrame(list(dfb['stats'])) 
# dfb2 = dfb1.loc[:,0:2].stack().reset_index()
# dfb3 = pd.DataFrame(list(dfb2[0]))
# dfb = dfb.rename(columns={'_id':'matchID'})
# cfb = pd.merge(dfb3, dfb, on='matchID')
# cfb['class for 1'] = cfb.loc[:,'stats_x'].apply(lambda x: x['top']['class'])
# cfb['win for 1'] = cfb.loc[:,'stats_x'].apply(lambda x: x['top']['winner'])
# cfb['class for 2'] = cfb.loc[:,'stats_x'].apply(lambda x: x['bottom']['class'])
# cfb['win for 2'] = cfb.loc[:,'stats_x'].apply(lambda x: x['bottom']['winner'])

# cfb = cfb[['player 1','player 2','class for 1','class for 2','win for 1','win for 2']]

# dictionary = alldf[['name','class 1','class 2','class 3','arc 1','arc 2','arc 3']].copy()
# for i in range (1,4):
#     dictionary[f'nameclass{i}'] = dictionary['name'] + dictionary[f'class {i}']
    
    
# nameclass = dictionary.loc[:,'nameclass1':'nameclass3'].stack().reset_index().rename(columns={0:'nameclass'})
# arche = dictionary.loc[:,'arc 1':'arc 3'].stack().reset_index().rename(columns={0:'archetype'})
# diction = pd.concat([nameclass, arche], axis=1)
# diction = diction[['nameclass','archetype']].set_index('nameclass')
# pa_dict = diction.to_dict()
 
# cfb['playerarc1'] = cfb['player 1']+ cfb['class for 1']
# cfb['playerarc2'] = cfb['player 2']+ cfb['class for 2']
# cfb['archetype 1'] = cfb.loc[:,'playerarc1'].apply(lambda x: pa_dict.get('archetype').get(x, 'Unknown Unknown'))
# cfb['archetype 2'] = cfb.loc[:,'playerarc2'].apply(lambda x: pa_dict.get('archetype').get(x, 'Unknown Unknown'))

# match = cfb[['archetype 1','archetype 2','win for 1','win for 2']]
# matchf1 = match[match['archetype 1'].str.contains('Unknown')==False]
# matchf2 = matchf1[matchf1['archetype 2'].str.contains('Unknown')==False]
# match1 = matchf2.loc[match['win for 1'] == True]
# match2 = matchf2.loc[match['win for 2'] == True]
# match1re = match1.reindex(columns=['archetype 1','archetype 2'])
# match2re = match2.reindex(columns=['archetype 2','archetype 1']).rename(columns={'archetype 2':'archetype 1', 'archetype 1':'archetype 2'})

# match1re['count'] = 1
# match111 = match1re.groupby(['archetype 1','archetype 2']).sum()

# allgame = pd.concat([match1re, match2re], ignore_index=True)
# allgame['count'] = 1
# allgamea = allgame.groupby(['archetype 1','archetype 2']).sum()

# allgameb =allgamea.reset_index()
# allgamec = allgameb['archetype 1'].append(allgameb['archetype 2']).value_counts().reset_index()

# allarc = allgamec['index'].tolist()
# allgamebmatrix = allgameb[['archetype 1', 'archetype 2', 'count']].values

# writer = pd.ExcelWriter('Excel_and_CSV/Win Count.xlsx')
# allgamea.to_excel(writer, 'Sheet1')
# writer.save()

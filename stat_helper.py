# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:19:41 2020
This is statistics helper module. Functions in this module will help to take care all the stuffs that needed 
to create clean excel/df based statistics
@author: zhiff
"""

import pandas as pd


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

def get_lineup_df(df):
    lineup = df["Lineup"].value_counts(normalize = False, ascending = False)
    lineup = lineup.rename_axis("Lineup").reset_index(name = 'Count')
    lineup['Player %'] = (round((lineup['Count']/(int(df.shape[0])))*100, 2))
    return lineup

def get_decks_df(df, maxdeck):
    decks = df.loc[:,'arc 1':f'arc {maxdeck}'].stack().value_counts(normalize = False, ascending = False)
    decks = decks.rename_axis("Deck Archetype").reset_index(name = 'Count')
    decks['Player %'] = (round((decks['Count']/(int(df.shape[0])))*100, 2))
    return decks

def add_statistics_tool(df):
    mean = round(df.mean(axis=1),2)
    median = df.median(axis=1)
    std = round(df.std(axis=1),2)
    df['Median'] = median
    df['Std Deviation'] = std
    df['Mean'] = mean
    return df

def get_popular_archetype(df, min_occurrence, maxdeck):
        
    # check the number of occurence (refer to statistics)
    decks =  get_decks_df(df, maxdeck)
    decks = decks.loc[decks['Count'] >= min_occurrence]
    popular_archetype = decks['Deck Archetype'].tolist()
    return popular_archetype

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
    dfa = dfa.rename(columns={'bannedClass':'class 1'})
    
    # Caluclate ban percentage
    dfd3c['totalban'] = dfd3c['ban 1'] + dfd3c['ban 2'] + dfd3c['ban 3']
    for i in range(1,4):
            dfd3c[f'ban {i} rate'] = round(dfd3c[f'ban {i}']/ dfd3c['totalban'], 2)
    
    dfd3c = dfd3c.fillna(0)
    return dfd3c

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

def get_win_ban_archetype(alldf):
    decks = alldf.loc[:,'arc 1':'arc 3'].stack().reset_index().rename(columns={0:'archetype'})
    bans = alldf.loc[:,'ban 1 rate':'ban 3 rate'].stack().reset_index().rename(columns={0:'ban percentage'})
    db = pd.concat([decks, bans], axis=1)[['archetype', 'ban percentage']]
    db = db.groupby('archetype').mean()
    db['ban percentage'] = round(db['ban percentage'], 4)
    
    wins = alldf.loc[:,'win 1':'win 3'].stack().reset_index().rename(columns={0:'win total'})
    matches =  alldf.loc[:,['total match 1','total match 2','total match 3']].stack().reset_index().rename(columns={0:'match total'})
    wr = pd.concat([decks, wins, matches], axis=1)[['archetype','win total','match total']]
    wr = wr.groupby('archetype').sum()
    wr['win percentage']= round(wr['win total']/wr['match total'], 4)
    
    winbanstats = pd.concat([wr,db], axis=1)
    winbanstats = winbanstats.fillna(0)
    return winbanstats
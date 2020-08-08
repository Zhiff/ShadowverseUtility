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

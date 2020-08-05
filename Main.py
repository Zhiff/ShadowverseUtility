# -*- coding: utf-8 -*-
"""
Spyder Editor


This is the main file
"""
import pandas as pd
import numpy as np
import openpyxl as oxl
from deckmodule import Deck
import xlsxwriter

 
# This function will quickly convert all raw svportal links that found in excel document into deck archetype link. regardless of format
# Input : excel file
# Output : new excel file
def excel_convert_quick(excelfile):
    excel = oxl.load_workbook(excelfile)
    sheet = excel['Sheet1']
    # Iterate all cells in excel sheet
    for column in range(1, sheet.max_column + 1):
        for row in range(1, sheet.max_row + 1):
            cell = sheet.cell(row, column)
            #We only care about svportal, so it must be a string
            if type(cell.value) == str:
                if 'shadowverse-portal.com' in cell.value:
                    #determine archetype by calling checker function, save old value into pure hyperlink, save archetype as the string description
                    deck = Deck(cell.value)
                    archetype = deck.archetype_checker()
                    cell.hyperlink = cell.value
                    cell.value = archetype
    
    excel.save('Excel_and_CSV/SVOFilteredDecks_View.xlsx')


# This function 
def excel_convert_dataset_3decks(svo_raw):
    df = pd.read_excel(svo_raw)
    df['arc 1'] = df['deck 1'].apply(lambda x: Deck(x).archetype_checker())
    df['arc 2'] = df['deck 2'].apply(lambda x: Deck(x).archetype_checker())
    df['arc 3'] = df['deck 3'].apply(lambda x: Deck(x).archetype_checker())
    df = add_lineup_column_3decks(df)
    writer = pd.ExcelWriter("Excel_and_CSV/SVOFilteredDecks_Data.xlsx")
    df.to_excel(writer, 'MainData')
    writer.save()
    
    
def add_lineup_column_3decks(df):
    # add new column which contains all 3 decks, then make them as Set to take care the uniformity
    df_added_lineup = df.assign(Lineup = list(zip(df['arc 1'],df['arc 2'],df['arc 3'],)) )
    df_added_lineup['Lineup'] = df_added_lineup['Lineup'].apply(set)
    return df_added_lineup
    

def get_lineup_df(df):
    lineup = df["Lineup"].value_counts(normalize = False, ascending = False)
    lineup = lineup.rename_axis("Lineup").reset_index(name = 'Count')
    lineup['Player %'] = (round((lineup['Count']/(int(df.shape[0])))*100, 2))
    return lineup


def get_decks_df(df):
    decks = df.loc[:,'arc 1':'arc 3'].stack().value_counts(normalize = False, ascending = False)
    decks = decks.rename_axis("Deck Archetype").reset_index(name = 'Count')
    decks['Player %'] = (round((decks['Count']/(int(df.shape[0])))*100, 2))
    return decks

def excel_statistics_3decks(svo_archetype):
    
    #Adding a new column in df called lineup. Lineup is basically a list of 3 decks that has been sorted ex : {sword, dragon, blood}
    df = pd.read_excel(svo_archetype)
    df = add_lineup_column_3decks(df)
    # Create a new dataframe that consists only lineup and their amount of occurrence
    lineup = get_lineup_df(df)
    #Create a new dataframe that consists only deck and their amount of occurrence
    decks = get_decks_df(df)

    writer = pd.ExcelWriter("Excel_and_CSV/Statistics.xlsx")
    lineup.to_excel(writer, "lineup")
    decks.to_excel(writer, "decks")
    writer.save()

#This function will create an excel document which consists of Deck Archetype Breakdowns
#The sheet will list all players decklist grouped by archetype and compare it side by side in order to get bigger picture of the archetype
def tournament_breakdown_3decks(svo_data):
    # read csv
    df = pd.read_excel(svo_data)
    # prepare excel output
    writer = pd.ExcelWriter("Excel_and_CSV/DeckBreakdown.xlsx")
    # check the number of occurence (refer to statistics)
    decks =  get_decks_df(df)
    decks = decks.loc[decks['Count'] >= 10]    
    popular_archetype = decks['Deck Archetype'].tolist()
    
    #Iterate each popular archetype
    for archetype in popular_archetype:
        flag_first = True   #Needed for first instance, resolve merge DF issue
        #Iterate the whole dataframe using i and x pointer
        for i in range(df.shape[0]): 
            for x in range(1,4):
                # accessing arc x column data ( x = 1,2,3 )
                decktype = df.loc[i,f'arc {x}']
                if (decktype == archetype):
                    # accessing name column and svlink portal column, then extract the details using function
                    player_name = df.loc[i,'name'] 
                    decklist = df.loc[i,f'deck {x}']
                    details = Deck(decklist).deck_details()
                    if flag_first == True:
                        #For the first instance, we simply initialize the data frame
                        arc_df = details.rename(columns={'Qty':player_name})
                        flag_first = False
                    else:
                        #Append dataframe with new dataframe
                        added_df = details.rename(columns={'Qty':player_name})
                        arc_df = pd.merge(arc_df, added_df, on='Name', how='outer')
        
        # cleanup dataframe by filling NaN into 0
        arc_df = arc_df.fillna(0)
        arc_df = arc_df.set_index('Name')
        
        #Add Mean, Median,and Standard Deviation into Dataframe
        mean = round(arc_df.mean(axis=1),2)
        median = arc_df.median(axis=1)
        std = round(arc_df.std(axis=1),2)
        arc_df['Median'] = median
        arc_df['Std Deviation'] = std
        arc_df['Mean'] = mean
        
        #Reordering Columns, Mean column appears in front
        cols = list(arc_df.columns.values)
        arc_df = arc_df[[cols[-1]] + cols[0:-1]]
        arc_df.to_excel(writer, archetype)
    
    writer.save()
    
    

#actual input. Just put the excel files that you want to convert here
excel_convert_quick('Excel_and_CSV/SVO SEAO JULY Cup 2020 ez viewing copy.xlsx')
excel_convert_dataset_3decks('Excel_and_CSV/SVO SEAO JULY Cup 2020 ez viewing copy.xlsx')
excel_statistics_3decks('Excel_and_CSV/SVOFilteredDecks_Data.xlsx')
tournament_breakdown_3decks('Excel_and_CSV/SVOFilteredDecks_Data.xlsx')





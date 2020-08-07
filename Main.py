# -*- coding: utf-8 -*-
"""
Spyder Editor


This is the main file
"""
import pandas as pd
import numpy as np
import openpyxl as oxl
import stat_helper as sh
from deckmodule import Deck
import requests
import json
 
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
    
    excel.save('Excel_and_CSV/FilteredDecks_View.xlsx')


# This function 
def excel_convert_dataset(svo_raw, maxdeck):
    df = pd.read_excel(svo_raw)
    for i in range(1, maxdeck+1):
        df[f'arc {i}'] = df[f'deck {i}'].apply(lambda x: Deck(x).archetype_checker())    
    if maxdeck == 3:
        df = sh.add_lineup_column_3decks(df)
        writer = pd.ExcelWriter("Excel_and_CSV/FilteredDecks_Data.xlsx")
    elif maxdeck == 2:
        df = sh.add_lineup_column_2decks(df)
        writer = pd.ExcelWriter("Excel_and_CSV/FilteredDecks_Data.xlsx")
    
    df.to_excel(writer, 'MainData')
    writer.save()

# requirements : name (lowercase) , deck 1 , deck 2 
def excel_statistics(svo_data, maxdeck):
    
    #Adding a new column in df called lineup. Lineup is basically a list of 3 decks that has been sorted ex : {sword, dragon, blood}
    df = pd.read_excel(svo_data)
    writer = pd.ExcelWriter("Excel_and_CSV/Statistics and Breakdown.xlsx")
    if maxdeck == 3:
        df = sh.add_lineup_column_3decks(df)        
    elif maxdeck == 2:
        df = sh.add_lineup_column_2decks(df) 
    
    # Create a new dataframe that consists only lineup and their amount of occurrence
    lineup = sh.get_lineup_df(df)
    lineup.to_excel(writer, "Lineups")
    
    #Create a new dataframe that consists only deck and their amount of occurrence
    decks = sh.get_decks_df(df, maxdeck)
    decks.to_excel(writer, "Decks")
    
    # Breakdown each archetype
    tournament_breakdown(df, writer, maxdeck)  

    writer.save()


#This function will create an excel document which consists of Deck Archetype Breakdowns
#The sheet will list all players decklist grouped by archetype and compare it side by side in order to get bigger picture of the archetype
def tournament_breakdown(df, excelwriter, maxdeck):
    
    #Popular archetype filter. Will return the list of popular archetype with specified minimum occurrence
    occurrence = 1
    popular_archetype = sh.get_popular_archetype(df, occurrence, maxdeck)
    
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
                        arc_df = pd.merge(arc_df, added_df, on='CardName', how='outer')
        
        # cleanup dataframe by filling NaN into 0
        arc_df = arc_df.fillna(0)
        arc_df = arc_df.set_index('CardName')
        
        #Add Mean, Median,and Standard Deviation into Dataframe
        arc_df = sh.add_statistics_tool(arc_df)
        
        #Reordering Columns, Mean column appears in front
        cols = list(arc_df.columns.values)
        arc_df = arc_df[[cols[-1]] + cols[0:-1]]
        arc_df.to_excel(excelwriter, archetype)
    

    
#actual input. Just put the excel files that you want to convert here
# excel_convert_quick('Excel_and_CSV/SVO SEAO JULY Cup 2020 ez viewing copy.xlsx')
# excel_convert_dataset('Excel_and_CSV/SVO SEAO JULY Cup 2020 ez viewing copy.xlsx', 3)
# excel_statistics('Excel_and_CSV/FilteredDecks_Data.xlsx', 3)

#Scrap data from MS Gaming in Battlefy
#requirements : Json link : //tournaments/..../teams . Can be found in response at Participants tab
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
    
    writer = pd.ExcelWriter('Excel_and_CSV/BFYImport.xlsx')
    df.to_excel(writer)
    writer.save()
        
    excel_convert_quick('Excel_and_CSV/BFYHacks.xlsx')
    excel_convert_dataset('Excel_and_CSV/BFYHacks.xlsx', 3)
    excel_statistics('Excel_and_CSV/SVOFilteredDecks_Data.xlsx', 3)


# # Read quick stats from top performers
# jsonlink = 'https://dtmwra1jsgyb0.cloudfront.net/stages/5f1266601047db149e9edf9e/latest-round-standings'
# response = requests.get(jsonlink)        
# data = response.json()
# df1 = pd.DataFrame(data)
# df2 = pd.DataFrame(list(df1['team'])).rename(columns={'_id':'teamID'})
# df = df1.merge(df2, on='teamID')
# df = df[['name', 'wins','losses','disqualified']]
# df = df.loc[(df['wins']>2) & (df['losses']<3) & (df['disqualified']== False)]

# alldata = pd.read_excel("Excel_and_CSV/FilteredDecks_Data.xlsx")
# dfdata = df.merge(alldata, on='name')
# dfview = dfdata[['name', 'wins','losses','arc 1','arc 2','arc 3']]


# writer = pd.ExcelWriter('Excel_and_CSV/TopCut_Data.xlsx')
# dfdata.to_excel(writer, 'Data')
# dfview.to_excel(writer, 'View')
# writer.save()

# excel_statistics('Excel_and_CSV/TopCut_Data.xlsx', 3)
# Blink = 'https://dtmwra1jsgyb0.cloudfront.net/stages/5f1266601047db149e9edf9e/stats'
# res1 = requests.get(Blink)
# data2 = res1.json()


# afalink = 'https://dtmwra1jsgyb0.cloudfront.net/stages/5f1266601047db149e9edf9e/matches'
# res = requests.get(afalink)
# data1 = res.json()
# dff = pd.DataFrame(data1)
# df1 = pd.DataFrame(list(dff['top']))
# df2 = pd.DataFrame(list(dff['bottom']))
# df3 = pd.DataFrame(data2)


jcglink = 'https://sv.j-cg.com/compe/view/entrylist/2314/json'
red = requests.get(jcglink)
data1 = red.json()
data2 = pd.DataFrame(list(data1['participants']))
data3 = data2.loc[data2['chk'] == 1]
data4 = pd.DataFrame(list(data3['dk'])).rename(columns={0:'deck 1',1:'deck 2'})

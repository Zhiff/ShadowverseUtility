# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 21:42:37 2020
This in excel module. This module will handle all data manipulation using in excel
@author: zhafi
"""
import pandas as pd
import openpyxl as oxl
import stat_helper as sh
from deckmodule import Deck


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

#This function will freeze first 2 column in statistics and highlight the important cards
def statistics_freeze_highlight(excelfile):
    excel = oxl.load_workbook(excelfile)
    breakdown = excel.sheetnames
    breakdown = breakdown[2:len(breakdown)]
    
    # Conditional Formatting, Highlight entire row if mean >= 2
    colorfill = oxl.styles.PatternFill(bgColor="A9A9A9")
    diffstyle = oxl.styles.differential.DifferentialStyle(fill=colorfill)
    rule = oxl.formatting.Rule(type='expression', dxf=diffstyle)
    rule.formula = ["$B2>=2"]

    for archetype in breakdown:
        sheet = excel[archetype]
        last_column = oxl.utils.cell.get_column_letter(sheet.max_column)
        sheet.freeze_panes = 'C1'
        sheet.conditional_formatting.add(f"A2:{last_column}80", rule)
    
    excel.save(excelfile)


# This function 
def excel_convert_dataset(svo_raw, maxdeck):
    df = pd.read_excel(svo_raw)
    for i in range(1, maxdeck+1):
        df[f'arc {i}'] = df[f'deck {i}'].apply(lambda x: Deck(x).archetype_checker())
    for i in range(1, maxdeck+1):
        df[f'class {i}'] = df[f'deck {i}'].apply(lambda x: Deck(x).class_checker_svo())
    if maxdeck == 3:
        df = sh.add_lineup_column_3decks(df)       
    elif maxdeck == 2:
        df = sh.add_lineup_column_2decks(df)
    
    writer = pd.ExcelWriter("Excel_and_CSV/FilteredDecks_Data.xlsx")
    df.to_excel(writer, 'MainData')
    writer.save()
    
# requirements : name (lowercase) , deck 1 , deck 2 
def excel_statistics(filtered_data, maxdeck):
    
    #Adding a new column in df called lineup. Lineup is basically a list of 3 decks that has been sorted ex : {sword, dragon, blood}
    df = pd.read_excel(filtered_data)        
    outputfile = "Excel_and_CSV/Statistics and Breakdown.xlsx"
    writer = pd.ExcelWriter(outputfile)
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
    statistics_freeze_highlight(outputfile)


#This function will create an excel document which consists of Deck Archetype Breakdowns
#The sheet will list all players decklist grouped by archetype and compare it side by side in order to get bigger picture of the archetype
def tournament_breakdown(df, excelwriter, maxdeck):
    
    #Popular archetype filter. Will return the list of popular archetype with specified minimum occurrence
    occurrence = 1
    popular_archetype = sh.get_popular_archetype(df, occurrence, maxdeck)
    
    #Iterate each popular archetype
    for archetype in popular_archetype:
        flag_first = True   #Needed for first instance, resolve merge DF issue
        if archetype != 'Unknown Unknown': #Only proceed with valid data
            #Iterate the whole dataframe using i and x pointer
            for i in range(df.shape[0]): 
                for x in range(1,maxdeck+1):
                    # accessing arc x column data ( x = 1,2,3 )
                    decktype = df.loc[i,f'arc {x}']
                    if (decktype == archetype):
                        # accessing name column and svlink portal column, then extract the details using function
                        player_name = df.loc[i,'name'] 
                        decklist = df.loc[i,f'deck {x}']
                        details = Deck(decklist).deck_details()
                        if details is not None: #Validity Check
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
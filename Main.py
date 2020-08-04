# -*- coding: utf-8 -*-
"""
Spyder Editor


This is the main file
"""
import pandas as pd
import numpy as np
import openpyxl as oxl
from deckmodule import Deck

 
# This function will quickly convert all raw svportal links that found in excel document into deck archetype link
# Input : excel file
# Output : new excel file
def excel_convert_all(excelfile):
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
    
    excel.save('Excel_and_CSV/SVOFilteredDecks.xlsx')

# This function 
def excel_convert_dataset_ready(svo_raw)
    
def add_lineup_column(df):
    # add new column which contains all 3 decks, then make them as Set to take care the uniformity
    df_added_lineup = df.assign(Lineup = list(zip(df['deck 1'],df['deck 2'],df['deck 3'],)) )
    df_added_lineup['Lineup'] = df_added_lineup['Lineup'].apply(set)
    return df_added_lineup
    

def excel_svo_statistics(svo_archetype):
    
    #Adding a new column in df called lineup. Lineup is basically a list of 3 decks that has been sorted ex : {sword, dragon, blood}
    df = pd.read_excel(svo_archetype)
    df = add_lineup_column(df)
    
    # Create a new dataframe that consists only lineup and their amount of occurrence
    lineup = df["Lineup"].value_counts(normalize = False, ascending = False)
    lineup = lineup.rename_axis("Lineup").reset_index(name = 'Count')
    lineup['Player %'] = (round((lineup['Count']/(int(df.shape[0])))*100, 2))
    
    #Create a new dataframe that consists only deck and their amount of occurrence
    decks = df.loc[:,'deck 1':'deck 3'].stack().value_counts(normalize = False, ascending = False)
    decks = decks.rename_axis("Deck Archetype").reset_index(name = 'Count')
    decks['Player %'] = (round((decks['Count']/(int(df.shape[0])))*100, 2))

    writer = pd.ExcelWriter("Excel_and_CSV/Statistics.xlsx")
    lineup.to_excel(writer, "lineup")
    decks.to_excel(writer, "decks")
    writer.save()
    
    
#actual input. Just put the excel files that you want to convert here
# excel_convert_all('Excel_and_CSV/SVO SEAO JULY Cup 2020 ez viewing copy.xlsx')
# excel_svo_statistics('Excel_and_CSV/SVOFilteredDecks.xlsx')

deck1 = Deck('https://shadowverse-portal.com/deck/3.4.6y7rA.6y7rA.6y7rA.6y4gM.6y4gM.6y4gM.6y9Yi.6y9Yi.6_up2.6_up2.6_up2.5_38w.5_38w.5_38w.6owk2.6owk2.6wbSI.6wbSI.6wgKo.6mj7Y.6mj7Y.6mj7Y.6uNs6.6uNs6.6uNs6.7007y.7007y.7007y.6y5Ow.6y5Ow.6y5Ow.6yAHQ.6yAHQ.6yAHQ.6y4g2.6y4g2.6y4g2.6yB-y.6yB-y.6yB-y?lang=en')
deck2 = Deck('https://shadowverse-portal.com/deck/3.4.6y7rA.6y7rA.6y7rA.6y4gM.6y4gM.6y4gM.6y9Yi.6y9Yi.6_up2.6_up2.6_up2.5_38w.5_38w.5_38w.6owk2.6owk2.6owk2.6mj7Y.6mj7Y.6mj7Y.6uNs6.6uNs6.6uNs6.6_xFI.7007y.7007y.7007y.6y5Ow.6y5Ow.6y5Ow.6yAHQ.6yAHQ.6yAHQ.6y4g2.6y4g2.6y4g2.6yB-y.6yB-y.6yB-y.6mlZo?lang=en#null')
df1 = deck1.deck_details()
df2 = deck2.deck_details()
df1 = df1.rename(columns={'Qty':'P1'})
df2 = df2.rename(columns={'Qty':'P2'})
                          
# df2 = df2.rename(columns={'Qty':'player 2'}
combi = pd.merge(df1, df2, on='Name', how='outer')
combi = combi.fillna(0)
print(combi)




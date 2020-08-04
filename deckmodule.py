# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 09:30:53 2020

@author: zhafi
"""
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 09:01:04 2020

@author: zhafi
"""
import pandas as pd

def somefunction():
    print("ayaya")
    
    

class Deck:
    
    def __init__(self, svlink, formats='rotation'):
        self.svlink = svlink
        self.formats = formats
        
    def class_checker(self):
        crafts = { 1 : 'Forestcraft' , 2 : 'Swordcraft' , 3 : 'Runecraft' , 4 : 'Dragoncraft' ,5 : 'Shadowcraft' , 6 : 'Bloodcraft' , 7 : 'Havencraft' , 8 : 'Portalcraft' }
        url = self.svlink
        if ('https://shadowverse-portal.com' in url):
            # Svportal syntax, class identity is the second number after the dot inside list
            classcode = url.split('.')[2] 
            craft_name = crafts.get(int(classcode)) #TRY
        else:
            craft_name = 'Unknown'
        
        return craft_name                
    
    
    ## Function to Identify the archetype by combination of cards
    ## input  : string. Sv portal links.
    ## output : string. Archetype name 
    def archetype_checker(self):
    
        # Initializes flags and iterator. If we found the archetype, we will set the flag to true. otherwise it will stays false
        found_flag = False
        i = 0
        # retrieve data frame from excel file that contains meta defining cards and its hash.
        # then store it into 2D array so we can process the data
        df = pd.read_excel('Excel_and_CSV/FortuneHandMeta.xlsx')
        cleaned_values = df[['Archetype Name', 'Hash Code 1', 'Hash Code 2','Hash Code 3']].values
        
        # Iterate each row in array
        for row in cleaned_values:
            # We define an archetype by ensuring there are 2 signature cards for that archetype. which is hashcode1 and hashcode2
            # we also check the non-existense of hashcode3 inside a deck to ensure it didn't conflict with other archetype
            # refer to excel sheet for details
            if ((cleaned_values[i][1] in self.svlink)&(cleaned_values[i][2] in self.svlink)&(cleaned_values[i][3] not in self.svlink)):
                #if we found matching archetype, set the flag to true, and set our archetype to archetype name that we will return
                found_flag = True
                archetype_name = cleaned_values[i][0]
                break
            i += 1
        
        if found_flag:
            archetype = archetype_name
        else:
            craft = self.class_checker()
            archetype = f"Unknown {craft}"
        
        return archetype
    
    
    def deck_details(self):
        cardhash = pd.read_csv('Excel_and_CSV/00_URLcode_JULY.csv')
        url = self.svlink
        if ('https://shadowverse-portal.com' in url):
            # Svportal syntax processing
            # 1. Remove the first URL part (http:shadowverse-portal~~) using split manipulation
            # 2. Remove the last URL part (~&lang=eng) 
            # 3. Arrange all hash into list and put it into dataframe
            removestart = url.split('.',3)[3]
            if '?' in removestart:
                cleanhash = removestart.split('?',1)[0]
            else :
                cleanhash = removestart.split('?',1)[0]
            decklist = cleanhash.split('.')
            df = pd.DataFrame(decklist)
            
            # Count the hash and create a 2D Lists Code : Qty
            df = df[0].value_counts().reset_index().rename(columns={'index':'Code', 0:'Qty'})
            
            # Match with the URLcode Reference document, then group it to resolve promotion card issue
            deck_df = pd.merge(df, cardhash)[['Name','Qty']]
            deck_df = deck_df.groupby('Name', as_index = False).agg('sum')
            
            return deck_df
        else:
            return None

    


# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 09:30:53 2020
This is Deck Module. This module contains Deck Class which store all info about the deck based on svportal url
@author: zhiff
"""

import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import pykakasi

class Deck:
    
    def __init__(self, svlink, formats='unlimited'):
        self.svlink = svlink
        self.formats = formats
        
    def class_checker(self):
        crafts = { 1 : 'Forest' , 2 : 'Sword' , 3 : 'Rune' , 4 : 'Dragon' ,5 : 'Shadow' , 6 : 'Blood' , 7 : 'Haven' , 8 : 'Portal' }
        url = self.svlink
        if ('https://shadowverse-portal.com/deck' in url):
            # Svportal syntax, class identity is the second number after the dot inside list
            classcode = url.split('.')[2] 
            craft_name = crafts.get(int(classcode)) #TRY
        else:
            craft_name = 'Unknown'
        
        return craft_name                
    
    def class_checker_svo(self):
        #This function is added to match battlefy class classification
        leader = { 'Forest':'arisa' , 'Sword':'erika' , 'Rune':'isabelle' , 'Dragon':'rowen' , 'Shadow':'luna' , 'Blood':'urias' , 'Haven':'eris' , 'Portal':'yuwan' }
        craft_me = self.class_checker()
        svo_class = leader.get(craft_me)
        
        return svo_class
        
        
    ## Function to Identify the archetype by combination of cards
    ## input  : string. Sv portal links.
    ## output : string. Archetype name 
    def archetype_checker(self):
    
        # Initializes flags and iterator. If we found the archetype, we will set the flag to true. otherwise it will stays false
        found_flag = False
        i = 0
        # retrieve data frame from excel file that contains meta defining cards and its hash.
        # then store it into 2D array so we can process the data
        if self.formats == 'rotation':
            df = pd.read_excel('Excel_and_CSV/RenascentMeta.xlsx')
            # df = pd.read_excel('Excel_and_CSV/RenascentMeta_Archetype_Korean.xlsx')
        elif self.formats == 'unlimited':
            df = pd.read_excel('Excel_and_CSV/UnlimitedMeta.xlsx')
        
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
        cardhash = pd.read_csv('Excel_and_CSV/generatedURLcode.csv')
        url = self.svlink
        if ('https://shadowverse-portal.com' in url):
            # Svportal syntax processing
            # 1. Remove the first URL part (http:shadowverse-portal~~) using split manipulation
            # 2. Remove the last URL part (~?lang=eng for deckbuilder ~&lang=eng for saved svportal) 
            # 3. Arrange all hash into list and put it into dataframe
            removestart = url.split('.',3)[3]
            if '?' in removestart:
                cleanhash = removestart.split('?',1)[0]
            elif '&' in removestart:
                cleanhash = removestart.split('&',1)[0]
            else:
                cleanhash = removestart

            decklist = cleanhash.split('.')
            df = pd.DataFrame(decklist)
            
            # Count the hash and create a 2D Lists Code : Qty
            df = df[0].value_counts().reset_index().rename(columns={'index':'Code', 0:'Qty'})
            
            # Match with the URLcode Reference document, then group it to resolve promotion card issue
            deck_df = pd.merge(df, cardhash)[['CardName','Qty']]
            deck_df = deck_df.groupby('CardName', as_index = False).agg('sum')
            
            return deck_df
        else:
            return None

    #function to add new cards into database by generating a csv file to be copied into main db
    def generate_svportalhash(self):
        filename = 'Excel_and_CSV/svportal.csv'
        url = self.svlink
        if ('deckbuilder' not in url):
            source = requests.get(url).text
            soup = bs(source, 'lxml')
            
            # Get Hash
            chash = soup.find('a', class_="deck-button l-block").get('href')
            cardlist = chash.split('.',2)[2]
            hashdf = pd.DataFrame(cardlist.split('.'))
            hashdf = hashdf.drop_duplicates().reset_index().drop(columns='index').rename(columns={0:'Code'})
            
            #Get Cost
            cost = soup.find_all('p', class_='el-card-list-cost')
            costlist = []
            for card in cost:
                cardcost = card.text
                costlist.append(int(cardcost))
            costdf = pd.DataFrame(costlist).rename(columns={0:'PP'})
            
            
            #Get Name
            name = soup.find_all('span', class_='el-card-list-info-name-text')
            namelist = []
            for card in name:
                cardname = card.text
                namelist.append(cardname)
            namedf = pd.DataFrame(namelist).rename(columns={0:'CardName'})
            
            #Get Rarity
            raritymap = { 'is-rarity-1':'Bronze', 'is-rarity-2':'Silver', 'is-rarity-3':'Gold', 'is-rarity-4':'Legendary'}
            rarity = soup.find_all('p', class_='el-card-list-rarity')
            rarelist = []
            for card in rarity:
                rarities = card.i.get('class')[1]
                maprare = raritymap[rarities]
                rarelist.append(maprare)
            raredf = pd.DataFrame(rarelist).rename(columns={0:'Rarity'})
            
            #Get Class
            craftmap = { '0':'Neutral', '1' : 'Forest' , '2' : 'Sword' , '3' : 'Rune' , '4' : 'Dragon' , '5' : 'Shadow' , '6' : 'Blood' , '7' : 'Haven' , '8' : 'Portal' }
            craft = soup.find_all('a', class_="el-icon-search is-small tooltipify")
            craftlist =[]
            for card in craft:
                # Craft code is the 4th digit of href, and 10th character in overall link
                craftcode = card.get('href')[9]
                mapcraft = craftmap[craftcode]
                craftlist.append(mapcraft)
            craftdf = pd.DataFrame(craftlist).rename(columns={0:'Class'})
            
            listdf = [craftdf, raredf, costdf, namedf, hashdf]
            alldf = pd.concat(listdf, axis=1)
            
            #Add all of them together in 1 dataframe
            alldf['Expansion'] = 'SOR'
            cols = list(alldf.columns.values)
            #Sorting so expansion name is in front
            alldf = alldf[[cols[-1]] + cols[0:-1]]
            
            alldf.to_csv(filename, index=False)

#deckbuilder -> saved decklist converter

    def deckbuilder_converter(self):
        sv = 'https://shadowverse-portal.com/deck/'
        lang_eng = '?lang=en'
        url = self.svlink
        if ('https://shadowverse-portal.com' in url):
            removestart = url.split('=')[1]
            cleanhash = removestart.split('&',1)[0]
            new_url = sv + cleanhash + lang_eng
            
        return new_url



def id_to_hash(uniqueID):
    a, b = divmod(uniqueID, 64)
    c, d = divmod(a, 64)
    e, f = divmod(c, 64)
    g, h = divmod(e, 64)
    
    hashes = ['','','','','']
    df = pd.read_csv('Excel_and_CSV/Base64.csv')
    alpha = df.to_dict("dict")
    hashes[4] = alpha.get("alphanumeric").get(b)
    hashes[3] = alpha.get("alphanumeric").get(d)
    hashes[2] = alpha.get("alphanumeric").get(f)
    hashes[1] = alpha.get("alphanumeric").get(h)
    hashes[0] = alpha.get("alphanumeric").get(g)
    
    finalhash = ''.join(hashes)
    return finalhash

def convert_kanji(text):
    kks = pykakasi.kakasi()
    kks.setMode('H','a')
    kks.setMode('K','a')
    kks.setMode('J','a')
    kks.setMode('r', 'Passport')
    kks.setMode('s', True)
    conv = kks.getConverter()
    result = conv.do(text)
    return result

# # json ='https://raw.githubusercontent.com/user6174/shadowverse-json/master/ja/all.json'

# json = 'https://raw.githubusercontent.com/user6174/shadowverse-json/master/en/all.json'
# response = requests.get(json)        
# data = response.json()
# dfa = pd.DataFrame(data)
# dfb = dfa.transpose()
# dfc = dfb[['expansion_','craft_','rarity_','pp_','name_','id_']]
# dffinal = dfc.copy()
# dffinal['id_'] =  dfc.loc[:,'id_'].apply(lambda x: id_to_hash(x))
# dffinal = dffinal.sort_index()
# dffinal = dffinal.rename(columns={'name_':'CardName', 'id_':'Code'})
# dffinal.to_csv('Excel_and_CSV/generatedURLcode.csv', index=False)

# jsonjp ='https://raw.githubusercontent.com/user6174/shadowverse-json/master/ja/all.json'
# response2 = requests.get(jsonjp)
# data2 = response2.json()
# ad = pd.DataFrame(data2).transpose()
# ae = ad.copy()
# ae['cv_romaji'] = ae.loc[:,'cv_'].apply(lambda x: convert_kanji(x))
# ae = ae[['cv_','cv_romaji']]
# ae = ae.sort_index()
# comp = pd.concat([dffinal,ae], axis=1)

# writer = pd.ExcelWriter('Excel_and_CSV/Seiyuu.xlsx')
# comp.to_excel(writer, index=False) 
# writer.save()

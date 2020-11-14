# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 05:28:15 2020

@author: YahikoSV
These modules are use to extract relevant take2 data (JCG only as of now)

"""

import website_scraper as ws
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs


#return the list of participants and all matches w/o default matches
def JCG_2pick_scraper(tcodes, analysis='single'):

    players_link_json = 'https://sv.j-cg.com/compe/view/entrylist/' + tcodes[0] + '/json'
    response = requests.get(players_link_json)
    data1 = response.json()
    data2 = pd.DataFrame(list(data1['participants']))
    data3 = data2.loc[data2['te'] == 1].reset_index() # Only filter those who checked in
    player_list = data3['nm'].reset_index().rename(columns={'nm':'Player'})
    player_list = player_list['Player']
    player_list_nodupe, dupe_list = rename_database_duplicates(player_list, data3)
    
    winner = []
    class_win = []
    
    for code in tcodes:
        bracket_link = 'https://sv.j-cg.com/compe/view/tour/' + code
        source = requests.get(bracket_link).text
        soup = bs(source, 'lxml')
        
        bracket = soup.select('li[onclick*="location"]')
        bracket_qty = len(bracket)
        round_link = bracket[0].get('onclick')
        first_round_number = int(round_link.split('/')[7])
    
        for match in range(0,bracket_qty):
            match_number = str(first_round_number + match)
            match_link = f'https://sv.j-cg.com/compe/view/match/{code}/{match_number}/'
            m_source = requests.get(match_link).text
            m_soup = bs(m_source, 'lxml')
            m_info = m_soup.select('span[style*="vertical"]')
            
            if bool(m_info) == True:
                
                if m_info[2].text in dupe_list:
                    winner_id = rename_JCGwinnername_duplicates(m_soup)
                    winner_name = f'{m_info[2].text} {winner_id}'
                    winner.append(winner_name)
                else:
                    winner.append(m_info[2].text)
                class_win.append(m_info[3].text)
            else:
                winner.append('No one')
                class_win.append('Default')
            #print(match)  #check if it's working
            
    winner_df = pd.DataFrame(winner).rename(columns={0:'Winner'})
    class_win_df = pd.DataFrame(class_win).rename(columns={0:'Class_Won'})
    listdf = [winner_df, class_win_df]
    alldf = pd.concat(listdf, axis=1)
    alldf_cleaned = alldf[alldf.Class_Won != 'Default']
    
    
    return player_list_nodupe, alldf_cleaned


#return the number of wins per class
def JCG_2pick_pickwin_index(matches):
    
    crafttranslate = { 'エルフ' : 'Forest' , 'ロイヤル' : 'Sword' , 'ウィッチ' : 'Rune' , 'ドラゴン' : 'Dragon', 'ネクロマンサー' : 'Shadow' , 'ヴァンパイア' : 'Blood' , 'ビショップ' : 'Haven' , 'ネメシス' : 'Portal' }  
    class_won_tally = matches["Class_Won"].value_counts().reset_index().rename(columns={'index':'Class', 'Class_Won':'No. of Wins'})
    
    class_won_percent = class_won_tally["No. of Wins"] / class_won_tally["No. of Wins"].sum() * 100
    class_won_percent = class_won_percent.round(2)
    class_won_tally['PickWin Percent'] = class_won_percent
    
    class_won_index = class_won_tally["No. of Wins"] / class_won_tally["No. of Wins"].sum() * 8
    class_won_index = class_won_index.round(2)
    class_won_tally['PickWin Index'] = class_won_index   
    class_won_tally = class_won_tally.replace({"Class": crafttranslate})
    
    return class_won_tally


#returns the the number of wins per class per player
def JCG_2pick_playerclass_win_count(players,matches):
    
    combined_tally = matches.value_counts().reset_index().rename(columns={0:'Count', 'Winner' : 'Player'})
    combined2_tally = matches["Winner"].value_counts().reset_index().rename(columns={'Winner':'Total','index':'Player'})
     
    forest_tally = combined_tally.loc[combined_tally['Class_Won'] == 'エルフ']
    forest_tally = forest_tally[['Player','Count']]
    
    sword_tally  = combined_tally.loc[combined_tally['Class_Won'] == 'ロイヤル']
    sword_tally = sword_tally[['Player','Count']]
    
    rune_tally   = combined_tally.loc[combined_tally['Class_Won'] == 'ウィッチ']
    rune_tally   = rune_tally[['Player','Count']]    
    
    dragon_tally = combined_tally.loc[combined_tally['Class_Won'] == 'ドラゴン']
    dragon_tally = dragon_tally[['Player','Count']]    
    
    shadow_tally = combined_tally.loc[combined_tally['Class_Won'] == 'ネクロマンサー']
    shadow_tally = shadow_tally[['Player','Count']]    
    
    blood_tally  = combined_tally.loc[combined_tally['Class_Won'] == 'ヴァンパイア']
    blood_tally = blood_tally[['Player','Count']]    
    
    haven_tally  = combined_tally.loc[combined_tally['Class_Won'] == 'ビショップ']
    haven_tally = haven_tally[['Player','Count']]    
    
    portal_tally = combined_tally.loc[combined_tally['Class_Won'] == 'ネメシス']
    portal_tally = portal_tally[['Player','Count']]

    player_tally = pd.merge(combined2_tally,players,on='Player',how='outer')
    
    player_tally = pd.merge(player_tally,forest_tally,on='Player',how='outer').rename(columns={'Count':'Forest'})
    player_tally = pd.merge(player_tally,sword_tally,on='Player',how='outer').rename(columns={'Count':'Sword'})
    player_tally = pd.merge(player_tally,rune_tally,on='Player',how='outer').rename(columns={'Count':'Rune'})
    player_tally = pd.merge(player_tally,dragon_tally,on='Player',how='outer').rename(columns={'Count':'Dragon'})
    player_tally = pd.merge(player_tally,shadow_tally,on='Player',how='outer').rename(columns={'Count':'Shadow'})
    player_tally = pd.merge(player_tally,blood_tally,on='Player',how='outer').rename(columns={'Count':'Blood'})
    player_tally = pd.merge(player_tally,haven_tally,on='Player',how='outer').rename(columns={'Count':'Haven'})
    player_tally = pd.merge(player_tally,portal_tally,on='Player',how='outer').rename(columns={'Count':'Portal'})
    player_tally = player_tally.fillna(0)
    
    return player_tally


def color_positive_green(val): 
    """ 
    Takes a scalar and returns a string with 
    the css property `'color: green'` for positive 
    strings, black otherwise. 
    """
    if val > 0: 
        color = 'green'
    else: 
        color = 'black'
    return 'color: %s' % color 


#save 2pick data into excel file + conditional formatting
def JCG_2pick_writer(tcode,pw_index,player_tally):
    
    tourney_link =  'https://sv.j-cg.com/compe/view/entrylist/' + tcode
    source = requests.get(tourney_link).text
    soup = bs(source, 'lxml')
    tourney_name_locate = soup.find_all('span', class_="nobr")
    tourney_name = f'JCG SV 2Pick {tourney_name_locate[3].text} {tourney_name_locate[5].text} {tourney_name_locate[6].text}'
    
    writer = pd.ExcelWriter(f"Excel_and_CSV/{tourney_name}.xlsx")
    pw_index.to_excel(writer, 'PickWin Index')
    player_tally.to_excel(writer, 'Player Tally')
    
    
    PW_sheet = writer.sheets['PickWin Index']
    PW_sheet.conditional_format('E2:E9', {'type': '3_color_scale', 'min_value' : 0, 'mid_value' : 1, 'max_value' : 8})
    PT_sheet = writer.sheets['Player Tally']
    PT_sheet.conditional_format('D2:K257', {'type': '2_color_scale', 'min_value' : 0, 'max_value' : 3, 'min_color': '#FFFFFF', 'max_color' :'#7FBA00'})
    writer.save()


#rename duplicate names into unique names    
def rename_database_duplicates(player_list, player_data):
    
    player_duplicate = player_list.value_counts().reset_index()
    duplicates = player_duplicate[player_duplicate['Player'] > 1]['index']
    
    dupe_list = list(duplicates)
    player_list_list = list(player_list)
    counter = 0
    for dupe_name in player_list_list:
        if dupe_name in dupe_list:
            row_locate = player_list_list.index(dupe_name, counter)
            id_no = player_data.loc[row_locate, 'id']
            player_list[row_locate] = f'{dupe_name} {id_no}'
            counter = row_locate + 1

    return player_list, dupe_list


#rename duplicate names of winner into respective unique names in a match  
def rename_JCGwinnername_duplicates(soup):
    
    score_board = soup.find("p", class_="score webfont")
    score = score_board = score_board.find_all("span")
    score_text = [score[0].text, score[1].text]
    winner_side = score_text.index('1')
    
    players = soup.find_all("a", class_="link-nodeco link-black hover-blue")
    winner_idlink = players[winner_side].get('href')
    winner_id = winner_idlink.split('=')[1]
    
    return winner_id

# tcodes = [ws.JCG_latest_tourney('2pick', 'group'), ws.JCG_latest_tourney('2pick', 'top16')]
# players, matches = JCG_2pick_scraper(tcodes, analysis='single')
# pw_index     = JCG_2pick_pickwin_index(matches)
# player_tally = JCG_2pick_playerclass_win_count(players,matches)
# JCG_2pick_writer(tcodes[0],pw_index,player_tally)
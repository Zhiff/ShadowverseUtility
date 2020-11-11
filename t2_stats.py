# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 05:28:15 2020

@author: owner
"""

import website_scraper as ws
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

tcode = ws.JCG_latest_tourney('2pick', 'group')
json = 'https://sv.j-cg.com/compe/view/entrylist/' + tcode + '/json'


def JCG_2pick_scraper(tcode, analysis='single'):

    players_link = 'https://sv.j-cg.com/compe/view/entrylist/' + tcode + '/json'
    response = requests.get(players_link)
    data1 = response.json()
    data2 = pd.DataFrame(list(data1['participants']))
    data3 = data2.loc[data2['te'] == 1] # Only filter those who checked in
    player_list = data3['nm'].reset_index().rename(columns={'nm':'Winner'})
    player_list = player_list['Winner']
    
    bracket_link = 'https://sv.j-cg.com/compe/view/tour/' + tcode 
    source = requests.get(bracket_link).text
    soup = bs(source, 'lxml')
    
    bracket = soup.select('li[onclick*="location"]')
    bracket_qty = len(bracket)
    round_link = bracket[0].get('onclick')
    first_round_number = int(round_link.split('/')[7])
    
    winner = []
    class_win = []
    
    for match in range(0,bracket_qty):
        match_number = str(first_round_number + match)
        match_link = f'https://sv.j-cg.com/compe/view/match/{tcode}/{match_number}/'
        m_source = requests.get(match_link).text
        m_soup = bs(m_source, 'lxml')
        m_info = m_soup.select('span[style*="vertical"]')
        
        if bool(m_info) == True:
            winner.append(m_info[2].text)
            class_win.append(m_info[3].text)
        else:
            winner.append('No one')
            class_win.append('Default')
        #print(match)
    winner_df = pd.DataFrame(winner).rename(columns={0:'Winner'})
    class_win_df = pd.DataFrame(class_win).rename(columns={0:'Class_Won'})
    listdf = [winner_df, class_win_df]
    alldf = pd.concat(listdf, axis=1)
    alldf_cleaned = alldf[alldf.Class_Won != 'Default']
    
    
    return player_list, alldf_cleaned



def JCG_2pick_pickwin_index(matches):
    #combined_tally = tally.value_counts().reset_index().rename(columns={0:'Count'})
    
    class_won_tally = matches["Class_Won"].value_counts().reset_index().rename(columns={'index':'Class', 'Class_Won':'No. of Wins'})
    
    class_won_percent = class_won_tally["No. of Wins"] / class_won_tally["No. of Wins"].sum() * 100
    class_won_percent = class_won_percent.round(2)
    class_won_tally['PickWin Percent'] = class_won_percent
    
    class_won_index = class_won_tally["No. of Wins"] / class_won_tally["No. of Wins"].sum() * 8
    class_won_index = class_won_index.round(2)
    class_won_tally['PickWin Index'] = class_won_index
    
    #unique_class_won_tally = combined_tally["Class_Won"].value_counts().reset_index().rename(columns={'index':'Class', 'Class_Won':'Unique Player Wins'})
    
    #unique_won_percent = unique_class_won_tally["Unique Player Wins"] / unique_class_won_tally["Unique Player Wins"].sum() * 100
    #unique_won_percent = unique_won_percent.round(2)

    
    return class_won_tally


def JCG_2pick_playerclass_win_count(players,matches):
    combined_tally = matches.value_counts().reset_index().rename(columns={0:'Count'})
    combined2_tally = matches["Winner"].value_counts().reset_index().rename(columns={'Winner':'Total','index':'Winner'})
    
    
    forest_tally = combined_tally.loc[combined_tally['Class_Won'] == 'エルフ']
    forest_tally = forest_tally[['Winner','Count']]
    
    sword_tally  = combined_tally.loc[combined_tally['Class_Won'] == 'ロイヤル']
    sword_tally = sword_tally[['Winner','Count']]
    
    rune_tally   = combined_tally.loc[combined_tally['Class_Won'] == 'ウィッチ']
    rune_tally   = rune_tally[['Winner','Count']]    
    
    dragon_tally = combined_tally.loc[combined_tally['Class_Won'] == 'ドラゴン']
    dragon_tally = dragon_tally[['Winner','Count']]    
    
    shadow_tally = combined_tally.loc[combined_tally['Class_Won'] == 'ネクロマンサー']
    shadow_tally = shadow_tally[['Winner','Count']]    
    
    blood_tally  = combined_tally.loc[combined_tally['Class_Won'] == 'ヴァンパイア']
    blood_tally = blood_tally[['Winner','Count']]    
    
    haven_tally  = combined_tally.loc[combined_tally['Class_Won'] == 'ビショップ']
    haven_tally = haven_tally[['Winner','Count']]    
    
    portal_tally = combined_tally.loc[combined_tally['Class_Won'] == 'ネメシス']
    portal_tally = portal_tally[['Winner','Count']]


    player_tally = pd.merge(combined2_tally,players,on='Winner',how='outer')
    
    player_tally = pd.merge(player_tally,forest_tally,on='Winner',how='outer').rename(columns={'Count':'Forest'})
    player_tally = pd.merge(player_tally,sword_tally,on='Winner',how='outer').rename(columns={'Count':'Sword'})
    player_tally = pd.merge(player_tally,rune_tally,on='Winner',how='outer').rename(columns={'Count':'Rune'})
    player_tally = pd.merge(player_tally,dragon_tally,on='Winner',how='outer').rename(columns={'Count':'Dragon'})
    player_tally = pd.merge(player_tally,shadow_tally,on='Winner',how='outer').rename(columns={'Count':'Shadow'})
    player_tally = pd.merge(player_tally,blood_tally,on='Winner',how='outer').rename(columns={'Count':'Blood'})
    player_tally = pd.merge(player_tally,haven_tally,on='Winner',how='outer').rename(columns={'Count':'Haven'})
    player_tally = pd.merge(player_tally,portal_tally,on='Winner',how='outer').rename(columns={'Count':'Portal'})
    player_tally = player_tally.fillna(0)
    

    return player_tally

def JCG_2pick_writer(pw_index,player_tally):
    
    writer = pd.ExcelWriter("Excel_and_CSV_Take2/JCG_Take2_Stats.xlsx")
    pw_index.to_excel(writer, 'PickWin Index')
    player_tally.to_excel(writer, 'Player Tally')
    writer.save()


players, matches = JCG_2pick_scraper(tcode, analysis='single')
pw_index     = JCG_2pick_pickwin_index(matches)
player_tally = JCG_2pick_playerclass_win_count(players,matches)
JCG_2pick_writer(pw_index,player_tally)
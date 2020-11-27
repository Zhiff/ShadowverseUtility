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
    player_list_nodupe = pd.DataFrame([player_list_nodupe,data3['id']]).transpose()
    
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
                if match == None: #When Special/Rare bug occurs
                    winner.append("Bug")
                    class_win.append('Bug')
                else:
                    if m_info[2].text in dupe_list:
                        winner_id = rename_JCGwinnername_duplicates(m_soup)
                        winner_name = f'{m_info[2].text} {winner_id}'
                        winner.append(winner_name)               
                    else:
                        winner.append(m_info[2].text)
                    class_win.append(m_info[3].text)
            else:
                winner_name = get_JCGwinnername_wonbydefault(m_soup)            
                winner.append(winner_name)
                class_win.append('Default')
            print(match)  #check if it's working
            
    winner_df = pd.DataFrame(winner).rename(columns={0:'Winner'})
    class_win_df = pd.DataFrame(class_win).rename(columns={0:'Class'})
    listdf = [winner_df, class_win_df]
    alldf = pd.concat(listdf, axis=1)
    
    return player_list_nodupe, alldf


#return the number of wins per class
def JCG_2pick_pickwin_index(matches):
    
    
    rank_order = pd.DataFrame(["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"],columns=['Rank'])
    class_names = pd.DataFrame(["Forest", "Sword", "Rune", "Dragon", "Shadow", "Blood", "Haven", "Portal"],columns=['Class'])
    crafttranslate = { 'エルフ' : 'Forest' , 'ロイヤル' : 'Sword' , 'ウィッチ' : 'Rune' , 'ドラゴン' : 'Dragon', \
                      'ネクロマンサー' : 'Shadow' , 'ヴァンパイア' : 'Blood' , 'ビショップ' : 'Haven' , 'ネメシス' : 'Portal' }  
    class_won_tally = matches["Class"].value_counts().reset_index().rename(columns={'index':'Class', 'Class':'No. of Wins'})
    class_won_tally = class_won_tally.replace({"Class": crafttranslate})

    class_won_tally = class_won_tally[class_won_tally.Class != 'Default']
    class_won_tally = pd.merge(class_names,class_won_tally,on='Class',how='outer').fillna(0)

    
    class_won_percent = class_won_tally["No. of Wins"] / class_won_tally["No. of Wins"].sum() * 100
    class_won_percent = class_won_percent.round(2)
    class_won_tally['PickWin Percent'] = class_won_percent
    
    class_won_index = class_won_tally["No. of Wins"] / class_won_tally["No. of Wins"].sum() * 8
    class_won_index = class_won_index.round(2)
    class_won_tally['PickWin Index'] = class_won_index   
    
    
    class_won_tally = class_won_tally.sort_values(by=['No. of Wins'], ascending=False).reset_index()
    class_won_tally = class_won_tally.drop(['index'], axis=1)
    class_won_tally = rank_order.join(class_won_tally)
    
    return class_won_tally


#returns the the number of wins per class per player
def JCG_2pick_playerclass_win_count(players,matches):
    
    rank = {'8':'Winner', '7' : 'Runner-up', '6' : 'Top 4', '5' : 'Top 8', '4' : 'Top 16', \
            '3' : 'Round4', '2' : 'Round3',  '1' : 'Round2', '0' : 'Round1'}
    crafttranslate = { 'エルフ' : 'Forest' , 'ロイヤル' : 'Sword' , 'ウィッチ' : 'Rune' , 'ドラゴン' : 'Dragon', \
                      'ネクロマンサー' : 'Shadow' , 'ヴァンパイア' : 'Blood' , 'ビショップ' : 'Haven' , 'ネメシス' : 'Portal' } 
    class_names = ["Forest", "Sword", "Rune", "Dragon", "Shadow", "Blood", "Haven", "Portal", "Default"]
    combined_tally = matches.value_counts().reset_index().rename(columns={0:'Count', 'Winner' : 'Player'})
    combined2_tally = matches["Winner"].value_counts().reset_index().rename(columns={'Winner':'Total','index':'Player'})
    combined_tally = combined_tally.replace({"Class": crafttranslate})
    player_tally = pd.merge(players,combined2_tally,on='Player',how='outer').sort_values(by=['Total'], ascending=False)
    
    for classes in class_names:
        class_tally = combined_tally.loc[combined_tally['Class'] == classes]
        class_tally = class_tally[['Player','Count']]
        player_tally = pd.merge(player_tally, class_tally,on='Player',how='outer').rename(columns={'Count':classes})
        
    player_tally = player_tally.fillna(0)
    rank_tally = pd.DataFrame([rank[str(int(x))] for x in player_tally["Total"]],columns=['Rank'])
    player_tally = rank_tally.join(player_tally)
    
    return player_tally


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
    PW_sheet.conditional_format('F2:F9', {'type': '2_color_scale', 'min_value' : 0, 'max_value' : 8})
    PW_sheet.write('C11', f'JCG SV 2Pick {tourney_name_locate[3].text}')
    PW_sheet.write('C12', f'{tourney_name_locate[5].text} {tourney_name_locate[6].text}')
    PW_sheet.write('D11', 'PW_index > 1')
    PW_sheet.write('D12', 'PW_index = 1')
    PW_sheet.write('D13', 'PW_index < 1')
    PW_sheet.write('E11', 'Popular and Winning')
    PW_sheet.write('E12', 'Average')
    PW_sheet.write('E13', 'Unpopular or Losing')
    
    PT_sheet = writer.sheets['Player Tally']
    PT_sheet.ignore_errors({'number_stored_as_text': 'D2:D258'})
    PT_sheet.freeze_panes(1,0)
    PT_sheet.conditional_format('F2:M257', {'type': '2_color_scale', 'min_value' : 0, 'max_value' : 3, 'min_color': '#FFFFFF', 'max_color' :'#7FBA00'})
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

#get the winner for those who won by default
def get_JCGwinnername_wonbydefault(soup):
    
    score_board = soup.find("p", class_="score webfont")
    score = score_board.find_all("span")
    score_text = [str(win) for win in score]
    winner_side = score_text.index('<span class="winner">0</span>')
    
    players = soup.find_all("a", class_="link-nodeco link-black hover-blue")
    winner_id= players[winner_side].text

    return winner_id

#Sample Note: JCG Nov. 25 Has a bug!
#tcodes = [ws.JCG_latest_tourney('2pick', 'group'), ws.JCG_latest_tourney('2pick', 'top16')]
#tcodes = ['2479','2499']
# players, matches = JCG_2pick_scraper(tcodes, analysis='single')
# pw_index = JCG_2pick_pickwin_index(matches)
# player_tally = JCG_2pick_playerclass_win_count(players,matches)
#JCG_2pick_writer(tcodes[0],pw_index,player_tally)
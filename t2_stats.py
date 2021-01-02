# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 05:28:15 2020

@author: YahikoSV
These modules are used to extract relevant take2 data (JCG only as of now)

"""
import pandas as pd
import requests
import sys
from bs4 import BeautifulSoup as bs


#Return 2 datasets
#1. Retrieve player name and their respective ID No.
#2. Retrieves every match with winner and class won
#3. If duplicate names are detected, they will be renamed in both datasets.
def JCG_2pick_scraper(tcodes, analysis='single'):

    players_link_json = 'https://sv.j-cg.com/compe/view/entrylist/' + tcodes[0] + '/json'
    response = requests.get(players_link_json)
    data1 = response.json()
    data2 = pd.DataFrame(list(data1['participants']))
    data3 = data2.loc[data2['te'] == 1].reset_index() # Only filter those who checked in
    player_list = data3['nm'].reset_index().rename(columns={'nm':'Player'})
    player_list = player_list['Player']
    player_list_nodupe, dupe_list = rename_database_duplicates(player_list, data3) #Find and rename duplicates with their ID
    player_data = pd.DataFrame([player_list_nodupe,data3['id']]).transpose() #1. Player name and their respective ID No.
    
    winner = []
    class_win = []
    
    #Opens every match link to check the winner and class won for #2
    #This loop extracts the match code for both tourneys
    there_is_error = False #Set to true if exception/error/bug occured
    for code in tcodes:
        bracket_link = 'https://sv.j-cg.com/compe/view/tour/' + code
        source = requests.get(bracket_link).text
        soup = bs(source, 'lxml')
        bracket = soup.select('li[onclick*="location"]')
        bracket_qty = len(bracket)
        round_link = bracket[0].get('onclick')
        first_round_number = int(round_link.split('/')[7])
        
        #Since match code has a pattern (+1) a loop is used to get all match links.
        for match in range(0,bracket_qty):
            match_number = str(first_round_number + match)
            match_link = f'https://sv.j-cg.com/compe/view/match/{code}/{match_number}/'
            m_source = requests.get(match_link).text
            m_soup = bs(m_source, 'lxml')
            m_info = m_soup.select('span[style*="vertical"]')
            
            #2. Retrieves every match with winner and class won
            if there_is_error == True and match_number == '530225':  #Edit when bug (sv.j-cg.com/compe/view/match/2481/528568/) occurs
                winner.append("ろさちい/silver")
                class_win.append('Default')       
            else:
                try:
                    winner_name, winner_side = get_winnername(m_soup, default = not bool(m_info))
                    if  winner_name in dupe_list:
                        winner_name = rename_JCGwinnername(m_soup, winner_name, winner_side)       
                    winner_class = str(m_info[3].text) if bool(m_info) == True else 'Default'
                    winner.append(winner_name)
                    class_win.append(winner_class)
                except Exception:
                    print(f'\n Cannot find match_info at code:{code} match:{match_number}')
                    print(f'Link: https://sv.j-cg.com/compe/view/match/{code}/{match_number}/')
                    print(str(sys.exc_info()[0]))
                    

            print(match, end = "\r")  #check if it's working
        
        #Create the dataset #2
        winner_df = pd.DataFrame(winner).rename(columns={0:'Winner'})
        class_win_df = pd.DataFrame(class_win).rename(columns={0:'Class'})
        list_df = [winner_df, class_win_df]
        match_data = pd.concat(list_df, axis=1)
    
    return player_data, match_data

#Return a dataset of the number of wins per class and other rescaled statistics.
def JCG_2pick_pickwin_index(matches):
    
    rank_order = pd.DataFrame(["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"],columns=['Rank'])
    class_names = pd.DataFrame(["Forest", "Sword", "Rune", "Dragon", "Shadow", "Blood", "Haven", "Portal"],columns=['Class'])
    crafttranslate = { 'エルフ' : 'Forest' , 'ロイヤル' : 'Sword' , 'ウィッチ' : 'Rune' , 'ドラゴン' : 'Dragon', \
                      'ネクロマンサー' : 'Shadow' , 'ヴァンパイア' : 'Blood' , 'ビショップ' : 'Haven' , 'ネメシス' : 'Portal' }  
    
    #Counts total wins for every class, Remove wins due to default
    class_won_tally = matches["Class"].value_counts().reset_index().rename(columns={'index':'Class', 'Class':'No. of Wins'})
    class_won_tally = class_won_tally.replace({"Class": crafttranslate})
    class_won_tally = class_won_tally[class_won_tally.Class != 'Default']
    class_won_tally = pd.merge(class_names,class_won_tally,on='Class',how='outer').fillna(0)

    #Add Class_Win %
    class_won_percent = class_won_tally["No. of Wins"] / class_won_tally["No. of Wins"].sum() * 100
    class_won_percent = class_won_percent.round(2)
    class_won_tally['PickWin Percent'] = class_won_percent
    
    #Add PW_Index
    class_won_index = class_won_tally["No. of Wins"] / class_won_tally["No. of Wins"].sum() * 8
    class_won_index = class_won_index.round(2)
    class_won_tally['PickWin Index'] = class_won_index   
    
    #Add rank_order
    class_won_tally = class_won_tally.sort_values(by=['No. of Wins'], ascending=False).reset_index()
    class_won_tally = class_won_tally.drop(['index'], axis=1)
    class_won_tally = rank_order.join(class_won_tally)
    
    return class_won_tally

#Returns dataset of the the Number of Wins per Class per Player
def JCG_2pick_playerclass_win_count(players,matches):
    

    crafttranslate = { 'エルフ' : 'Forest' , 'ロイヤル' : 'Sword' , 'ウィッチ' : 'Rune' , 'ドラゴン' : 'Dragon', \
                      'ネクロマンサー' : 'Shadow' , 'ヴァンパイア' : 'Blood' , 'ビショップ' : 'Haven' , 'ネメシス' : 'Portal' } 
    class_names = ["Forest", "Sword", "Rune", "Dragon", "Shadow", "Blood", "Haven", "Portal", "Default"]
    
    #Counts total wins per player
    combined_tally = matches.value_counts().reset_index().rename(columns={0:'Count', 'Winner' : 'Player'})
    combined2_tally = matches["Winner"].value_counts().reset_index().rename(columns={'Winner':'Total','index':'Player'})
    combined_tally = combined_tally.replace({"Class": crafttranslate})
    player_tally = pd.merge(players,combined2_tally,on='Player',how='outer')
    
    #Adds no. of wins per class per player
    for classes in class_names:
        class_tally = combined_tally.loc[combined_tally['Class'] == classes]
        class_tally = class_tally[['Player','Count']]
        player_tally = pd.merge(player_tally, class_tally,on='Player',how='outer').rename(columns={'Count':classes})
    

    player_tally = player_tally.fillna(0)

       
    return player_tally


def add_player_rank(player_tally):
    
    rank = {'8':'Winner', '7' : 'Runner-up', '6' : 'Top 4', '5' : 'Top 8', '4' : 'Top 16', \
        '3' : 'Round 4', '2' : 'Round 3', '1' : 'Round 2', '0' : 'Round 1'}
    #Add rank
    player_tally = player_tally.sort_values(by=['Total'], ascending=False)
    rank_tally = pd.DataFrame([rank[str(int(x))] for x in player_tally["Total"]],columns=['Rank'])
    player_tally = rank_tally.join(player_tally)
    
    return player_tally

#Save 2pick data into excel file + some formatting
def JCG_2pick_writer(tcode,pw_index,player_tally):
    
    tourney_link =  'https://sv.j-cg.com/compe/view/entrylist/' + tcode
    source = requests.get(tourney_link).text
    soup = bs(source, 'lxml')
    tourney_name_locate = soup.find_all('span', class_="nobr")
    tourney_name = f'JCG SV 2Pick {tourney_name_locate[3].text} {tourney_name_locate[5].text} {tourney_name_locate[6].text}'
    
    writer = pd.ExcelWriter(f"Excel_and_CSV/{tourney_name}.xlsx")
    pw_index.to_excel(writer, 'PickWin Index')
    player_tally.to_excel(writer, 'Player Tally')
    
    #PickWin Index
    PW_sheet = writer.sheets['PickWin Index']
    PW_sheet.conditional_format('F2:F9', {'type': '2_color_scale', 'min_value' : 0, 'max_value' : 8})
    
    #Player Tally
    PT_sheet = writer.sheets['Player Tally']
    PT_sheet.ignore_errors({'number_stored_as_text': 'D2:D258'})
    PT_sheet.freeze_panes(1,0)
    PT_sheet.conditional_format('F2:M257', {'type': '2_color_scale', 'min_value' : 0, 'max_value' : 3, 'min_color': '#FFFFFF', 'max_color' :'#7FBA00'})
    

    writer.save()

#Rename duplicate names by adding their respective ID No. to their names
def rename_database_duplicates(player_list, player_data):
    
    #Create a list of duplicate names as basis
    player_duplicate = player_list.value_counts().reset_index()
    duplicates = player_duplicate[player_duplicate['Player'] > 1]['index']
    
    #Check if name has duplicate and rename them.
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

#Find the which side won and get the winner's name
def get_winnername(soup, default):
    
    #Locate if the winner is left or right
    score_board = soup.find("p", class_="score webfont")
    score = score_board.find_all("span")
    score_text = [str(win) for win in score]
    
    if default == False:
        winner_side = score_text.index('<span class="winner">1</span>')
    else:
        winner_side = score_text.index('<span class="winner">0</span>') 
    
    #Get winner name
    players = soup.find_all("a", class_="link-nodeco link-black hover-blue")
    winner_name= players[winner_side].text

    return winner_name, winner_side

#Rename duplicate names of winner by adding their respective ID No. in match links
def rename_JCGwinnername(soup, winner_name, winner_side):
    
    players = soup.find_all("a", class_="link-nodeco link-black hover-blue")                              
    winner_idlink = players[winner_side].get('href')
    winner_id = winner_idlink.split('=')[1]
    winner_name = f'{winner_name} {winner_id}'
        
    return winner_name
        
#Check for players that change names  
def rename_changednames(player_tally, tcodes):
    
    zero_id_player = []
    player_index = []
    
    for player in player_tally.index:
        if player_tally['id'][player] == 0:  #Name change detected
            zero_id_player.append(player_tally['Player'][player])
            player_index.append(player)
    
    #Open Finals Enterylist
    if bool(zero_id_player) == True:
        pd.set_option('mode.chained_assignment', None)
        players_link_json = 'https://sv.j-cg.com/compe/view/entrylist/' + tcodes[1] + '/json'
        response = requests.get(players_link_json)
        data1 = response.json()
        data2 = pd.DataFrame(list(data1['participants']))
        final_tally = data2[['nm','id']]
        
        for player in range (0,len(zero_id_player)):       
            #Link the 2 data frames 
            final_player_name = zero_id_player[player]
            final_player_id = str(int(final_tally[final_tally['nm']==final_player_name]['id']))
            final_player_index = player_index[player]
            
            group_player_index = int(player_tally.index[player_tally['id'] == final_player_id].tolist()[0])
            group_player_name = player_tally['Player'][group_player_index]
            
            #rename elements
            player_tally['Player'][group_player_index] = f'{final_player_name} [{group_player_name}]'
            player_tally['Player'][final_player_index] = f'{final_player_name} [{group_player_name}]'
            player_tally['id'][final_player_index] = final_player_id       
    
        #Combine rows with same name and ID
        player_tally = player_tally.fillna(0)
        player_tally = player_tally.groupby(["Player","id"]).sum()
        player_tally = player_tally.sort_values(by=['Total'], ascending=False).reset_index()
        
    return player_tally
    

#Run function for JCG T2
def JCG_T2_scraper(tcodes):
    
    players, matches = JCG_2pick_scraper(tcodes, analysis='single')
    pw_index = JCG_2pick_pickwin_index(matches)
    player_tally = JCG_2pick_playerclass_win_count(players,matches)
    player_tally = rename_changednames(player_tally,tcodes)
    player_tally = add_player_rank(player_tally)
    JCG_2pick_writer(tcodes[0],pw_index,player_tally)   
      
    
# -*- coding: utf-8 -*-
"""
This is JCG Helper module. All sub-scraper related to Jcg website will be performed in this module

"""

import pandas as pd
import requests
from deckmodule import Deck
from bs4 import BeautifulSoup as bs
import numpy as np
import json
import stat_helper as sh
import excel_module as em

def grabjsonfromHTML(tcode):
    entrieslink = 'https://sv.j-cg.com/competition/' + tcode + '/entries'
    source = requests.get(entrieslink).text
    soup = bs(source, 'lxml')
    
    # Find and extract JSON file in HTML
    all_scripts = soup.find_all('script')
    
    #currently hardcasted, faster processing but will be screwed when website changes
    dljson = all_scripts[7].string
    
    #cleaning string to comply with JSON format
    cleanedjson = dljson[dljson.find('list'):dljson.find('listFiltered')]
    finaljson = cleanedjson.replace('list:','').strip()[:-1]
    
    data = json.loads(finaljson)
    df = pd.DataFrame(data)
    return df

def cleanjson(jsondf):
    sv = 'https://shadowverse-portal.com/deck/'
    lang_eng = '?lang=en'
    data1 = jsondf.loc[jsondf['result']==1].copy()
    data1['d1'] = data1['sv_decks'].apply(lambda x: x[0]['hash'] if x else None)
    data1['d2'] = data1['sv_decks'].apply(lambda x: x[1]['hash'] if x else None)
    data1['deck 1']= data1['d1'].apply(lambda x: sv + x + lang_eng if x else 'Invalid Deck')
    data1['deck 2']= data1['d2'].apply(lambda x: sv + x + lang_eng if x else 'Invalid Deck')
    data2 = data1[['name','deck 1','deck 2']].copy()
    data3 = sh.handle_duplicate_row(data2, 'name').reset_index().drop(['index'], axis=1)
    return data3

def group_winner_check(tcode):

    resultpage = 'https://sv.j-cg.com/competition/' + tcode + '/results'
    source = requests.get(resultpage).text
    soup = bs(source, 'lxml')
        
    names = []
    deck1 = []
    deck2 = []
        
    firstplace = soup.find_all('div', class_='result result-1')
    
    for user in firstplace:
        # Add their name into array
        name = user.find('div', class_='result-name').text
        names.append(name)
        
        # Add their decks into array
        links = user.find_all('a')
        for link in links[1::3]:
            decks = link.get('href')
            deck1.append(decks)
        for link in links[2::3]:
            decks = link.get('href')
            deck2.append(decks)
    
    df = pd.DataFrame([names,deck1,deck2]).transpose().rename(columns={0:'name', 1:'arc 1', 2:'arc 2'})    
    return df

def isTournamentOver(tcode, stage):
    tstate = False
    resultpage = 'https://sv.j-cg.com/competition/' + tcode + '/results'
    source = requests.get(resultpage).text
    soup = bs(source, 'lxml')
    placement = soup.find_all('div', class_="result result-1")
    if (placement != None):
        if stage == 'group' and (len(placement)>2):
            tstate = True
        elif stage == 'top16' and (len(placement)==1):
            tstate = True
            
    return tstate

def bracketidfinder(tcode):
    bracketpage = 'https://sv.j-cg.com/competition/' + tcode + '/bracket'
    source = requests.get(bracketpage).text
    soup = bs(source, 'lxml')
    
    allscr = soup.find_all('script')
    
    tjson = allscr[7].text
    cleanedjson = tjson[tjson.find('"groups":['):tjson.find('],"myUsername"')]
    finaljson = cleanedjson.replace('"groups":[','')
    bracketid = json.loads(finaljson)['id']
    bracketid = str(bracketid)
    return bracketid

def retrieveTop16JCG(bracketid, tcode):
    bracketjson = 'https://sv.j-cg.com/api/competition/group/' + bracketid
    response = requests.get(bracketjson)    
    data = response.json()['rounds']
    # name = data[0]['matches'][0]['teams'][0]['name']
    
    namelist = []
    # Add all name in the bracket into one list, the more occurence, the higher the ranking.
    for i in range(len(data)):
        matches = data[i]['matches']
        for j in range(len(matches)):
            teams = matches[j]['teams']
            for k in range(len(teams)):
                try:
                    name = teams[k]['name']
                except TypeError:
                    name = ''

                namelist.append(name)
    
    namedf = pd.DataFrame(namelist).rename(columns={0:'name'})
    namedf = namedf['name'].value_counts().rename_axis("name").reset_index(name = 'Count')
    
    
    resultpage = 'https://sv.j-cg.com/competition/' + tcode + '/results'
    source = requests.get(resultpage).text
    soup = bs(source, 'lxml')
    
    user1 = soup.find('div', class_='result result-1')
    firstplace = user1.find('div', class_='result-name').text
    user2 = soup.find('div', class_='result result-2')
    secondplace = user2.find('div', class_='result-name').text
    
    namedf.at[0,'name'] = firstplace
    namedf.at[1,'name'] = secondplace
    
    return namedf

def scrapseasonIDs(sv_format, season):
    maxpage = 10
    jcgids = []
    dates = []
    
    for page in range(maxpage):
        linkschedule = 'https://sv.j-cg.com/past-schedule/' + sv_format + '?page=' + str(page+1)
        source = requests.get(linkschedule).text
        soup = bs(source, 'lxml')
        currentlink = soup.find_all('a', class_='schedule-link')
        
        for link in currentlink:
            jcglink = link.get('href')
            tcode = jcglink.split('/')[4]
            title = link.find('div', class_='schedule-title').text
            date = title[title.find('V'):(title.find('日'))+1]
            if ('グループ予選' in title) and (season in title):
            # if ('決勝トーナメント' in title) and (season in title):
                jcgids.append(tcode)
                dates.append(date)
                
    
    jcgids.reverse()
    dates.reverse()
    return jcgids, dates

def get_top16_view(tcode):

    resultpage = 'https://sv.j-cg.com/competition/' + tcode + '/results'
    source = requests.get(resultpage).text
    soup = bs(source, 'lxml')
    
    profile = []
    names = []
    deck1 = []
    deck2 = []
        
    firstplace = soup.find_all('div', class_='result result-1')
    
    for user in firstplace:
        # Add their name into array
        name = user.find('div', class_='result-name')
        names.append(name.text)
        
        prof = name.find('a').get('href')
        profile.append(prof)
        
        # Add their decks into array
        links = user.find_all('a')
        for link in links[1::3]:
            decks = link.get('href')
            deck1.append(decks)
        for link in links[2::3]:
            decks = link.get('href')
            deck2.append(decks)
    
    df = pd.DataFrame([profile,names,deck1,deck2]).transpose().rename(columns={0:'profile', 1:'name', 2:'deck 1', 3:'deck 2'}) 
    df['name'] = '=HYPERLINK("' + df['profile'] + '", "' + df['name'] + '")' 
    df = df[['name','deck 1','deck 2']]
    group = pd.DataFrame({'Group':['Group 1','Group 2','Group 3','Group 4','Group 5','Group 6','Group 7','Group 8','Group 9','Group 10','Group 11','Group 12','Group 13','Group 14','Group 15','Group 16']})
    df = pd.concat([group, df],axis=1)
    return df

def get_deck_profile(tcode):
    entrieslink = 'https://sv.j-cg.com/competition/' + tcode + '/entries'
    source = requests.get(entrieslink).text
    soup = bs(source, 'lxml')
    # Find and extract JSON file in HTML
    all_scripts = soup.find_all('script')
    #currently hardcasted, faster processing but will be screwed when website changes
    dljson = all_scripts[7].string
    #cleaning string to comply with JSON format
    cleanedjson = dljson[dljson.find('list'):dljson.find('listFiltered')]
    finaljson = cleanedjson.replace('list:','').strip()[:-1]
    data = json.loads(finaljson)
    jsondf = pd.DataFrame(data)
    
    sv = 'https://shadowverse-portal.com/deck/'
    jcg = 'https://sv.j-cg.com/user/'
    lang_eng = '?lang=en'
    data1 = jsondf.loc[jsondf['result']==1].copy()
    data1['d1'] = data1['sv_decks'].apply(lambda x: x[0]['hash'] if x else None)
    data1['d2'] = data1['sv_decks'].apply(lambda x: x[1]['hash'] if x else None)
    data1['deck 1']= data1['d1'].apply(lambda x: sv + x + lang_eng if x else 'Invalid Deck')
    data1['deck 2']= data1['d2'].apply(lambda x: sv + x + lang_eng if x else 'Invalid Deck')
    data1['profile']=data1['nicename'].apply(lambda x: jcg + x)
    data2 = data1[['profile','name','deck 1','deck 2']].copy()
    df = data2
    
    print("end of entry gatherings")
    return df

def create_master_df(entry_df):
    
    df = sh.handle_duplicate_row(entry_df, 'name').reset_index().drop(['index'], axis=1)

    for i in range(1, 3):
        df[f'arc {i}'] = df[f'deck {i}'].apply(lambda x: Deck(x).archetype_checker())
    for i in range(1, 3):
        df[f'class {i}'] = df[f'deck {i}'].apply(lambda x: Deck(x).class_checker())     
    df = sh.add_lineup_column_2decks_class(df)
    df = sh.add_lineup_column_2decks(df) # Base Entries : Filtered-Deck-Data

    print("end of entry initialization")

    # preparation for Lineup
    dfc = df[['profile', 'Lineup']]
    dfc = dfc.set_index('profile')
    lineupdict = dfc.to_dict() 
    return (df, lineupdict)

def gather_match_id(tcode, stage):
    #Collecting MatchIDs for Result pages
    matchids = []

    #get info from the whole bracket
    bracketpage = 'https://sv.j-cg.com/competition/' + tcode + '/bracket'
    source = requests.get(bracketpage).text
    soup = bs(source, 'lxml')
    allscr = soup.find_all('script')
    
    if 'top16' in stage:
        #Specify the exact JSON inside the bracket and cleaning up
        tjson = allscr[7].text
        cleanedjson = tjson[tjson.find('"groups":['):tjson.find('],"myUsername"')]
        finaljson = cleanedjson.replace('"groups":[','')
        bracketid = json.loads(finaljson)['id']
        bracketid = str(bracketid)

        bracketjson = 'https://sv.j-cg.com/api/competition/group/' + bracketid
        bracketresponse = requests.get(bracketjson)    
        bracketdata = bracketresponse.json()['rounds']
        for j in range(len(bracketdata)):
            groupdata = bracketdata[j]['matches']
            for k in range(len(groupdata)):
                matchid = groupdata[k]['id']
                matchids.append(str(matchid))
    else:
        #Clean the Json for 16 group stage
        tjson = allscr[7].text
        cleanedjson = tjson[tjson.find('"groups":['):tjson.find('],"myUsername"')]
        finaljson = '{' + cleanedjson + ']}'
        bracket = json.loads(finaljson)
        # traverse the JSON to find each bracket ID , and furthermore match ID
        for i in range(16): #Groupstage has 16 group
            bracketid = bracket['groups'][i]['id']
            bracketid = str(bracketid)

            bracketjson = 'https://sv.j-cg.com/api/competition/group/' + bracketid
            bracketresponse = requests.get(bracketjson)    
            bracketdata = bracketresponse.json()['rounds']
            for j in range(len(bracketdata)):
                groupdata = bracketdata[j]['matches']
                for k in range(len(groupdata)):
                    matchid = groupdata[k]['id']
                    matchids.append(str(matchid))
    
    print("end of MatchID gatherings")
    return matchids



def create_matches_dataset(matchids):
    #Collecting Matches Record
    P1 = []
    P2 = []
    ResultP1 = []
    ResultP2 = []
    counter = 0
    print("Start of Match dataset building process")
    for match in matchids:
        counter = counter + 1
        print("Processing match number ", counter)
        matchjson = 'https://sv.j-cg.com/api/competition/match/' + match
        matchresponse = requests.get(matchjson)
        matchdata = matchresponse.json()
        if len(matchdata['teams']) > 1: #Check if it is not a bye round
            Player1 = 'https://sv.j-cg.com/user/' + matchdata['teams'][0]['nicename']
            P1.append(Player1)
            Player2 = 'https://sv.j-cg.com/user/' + matchdata['teams'][1]['nicename']
            P2.append(Player2)
            PR1 = matchdata['teams'][0]['won']
            ResultP1.append(PR1)
            PR2 = matchdata['teams'][1]['won']
            ResultP2.append(PR2)
        else:
            Player1 = 'https://sv.j-cg.com/user/' + matchdata['teams'][0]['nicename']
            P1.append(Player1)
            P2.append(np.nan)
            PR1 = matchdata['teams'][0]['won']
            ResultP1.append(PR1)
            ResultP2.append(0)

    print("Match Dataset has been completed")
    return P1, P2, ResultP1, ResultP2
    
def publish_final_standings(entry_df, P1, P2, ResultP1, ResultP2):
    # A. Wins Dataset Creation
    Players = P1 + P2
    Wins = ResultP1 + ResultP2
    WinDS1 = pd.DataFrame([Players,Wins]).transpose().rename(columns={0:'profile', 1:'win'})
    WinDS = WinDS1.groupby('profile')['win'].sum().reset_index().sort_values('win', ascending=False)

    # Overall Players View

    OverallP1 = pd.merge(entry_df, WinDS, how='left').sort_values('win', ascending=False, ignore_index=True)
    OverallP1['name'] = '=HYPERLINK("' + OverallP1['profile'] + '", "' + OverallP1['name'] + '")' 
    OverallView_df = OverallP1[['name','deck 1','deck 2','win']]

    rankings = pd.DataFrame({'Rank':['1st','2nd','3rd/4th','3rd/4th','5th-8th','5th-8th','5th-8th','5th-8th','9th-16th','9th-16th','9th-16th','9th-16th','9th-16th','9th-16th','9th-16th','9th-16th']})
    final_standings_df = pd.concat([rankings, OverallView_df],axis=1).dropna()

    outputfile = "Excel_and_CSV/FinalStandings.xlsx"
    writer = pd.ExcelWriter(outputfile)
    final_standings_df.to_excel(writer, sheet_name='Final Standings', index=False, startrow = 0, startcol = 0)
    writer.save()

    em.excel_convert_custom(outputfile, 2, True)
    em.add_class_color_custom(outputfile, 0, 2)
    print("FinalStandings.xlsx is ready")

def get_overall_view(master_df, P1, P2, ResultP1, ResultP2):
    # Wins Dataset Creation
    Players = P1 + P2
    Wins = ResultP1 + ResultP2
    WinDS1 = pd.DataFrame([Players,Wins]).transpose().rename(columns={0:'profile', 1:'win'})
    WinDS = WinDS1.groupby('profile')['win'].sum().reset_index().sort_values('win', ascending=False)

    # Overall Players View

    OverallP1 = pd.merge(master_df, WinDS, how='left').sort_values('win', ascending=False, ignore_index=True)
    OverallP1['name'] = '=HYPERLINK("' + OverallP1['profile'] + '", "' + OverallP1['name'] + '")' 
    OverallView_df = OverallP1[['name','deck 1','deck 2','win']]

    print("Overall View Dataset is ready")
    return OverallView_df


def get_matchup_view(lineupdict, P1, P2, ResultP1, ResultP2): 
    # # 2. Matchup Dataset
    Matches1 = pd.DataFrame([P1,P2,ResultP1,ResultP2]).transpose().rename(columns={0:'player 1', 1:'player 2', 2:'WinP1', 3:'WinP2'})
    Matches1 = Matches1.dropna()
    Matches1['player 1'] = Matches1.loc[:,'player 1'].apply(lambda x: lineupdict['Lineup'][x])
    Matches1['player 1'] = Matches1.loc[:,'player 1'].apply(lambda x: ' - '.join(x))
    Matches1 = Matches1.rename(columns={'player 1':'Lineup 1'})
    Matches1['player 2'] = Matches1.loc[:,'player 2'].apply(lambda x: lineupdict['Lineup'][x])
    Matches1['player 2'] = Matches1.loc[:,'player 2'].apply(lambda x: ' - '.join(x))
    Matches1 = Matches1.rename(columns={'player 2':'Lineup 2'})

    Matches_Base = Matches1.copy()   

    Base = Matches_Base.groupby(['Lineup 1','Lineup 2']).sum().reset_index()

    Flipped = Base.reindex(columns=['Lineup 2','Lineup 1','WinP2','WinP1'])
    Flipped = Flipped.rename(columns={'Lineup 2':'Lineup 1', 'Lineup 1':'Lineup 2','WinP2':'WinP1','WinP1':'WinP2' })

    Doubles = pd.concat([Base, Flipped], ignore_index=True)
    Doubles = Doubles.groupby(['Lineup 1','Lineup 2']).sum().reset_index()
    Doubles = Doubles.sort_values('WinP1', ascending=False, ignore_index=True)

    Doubles['Zip'] = list(zip(Doubles['Lineup 1'], Doubles['Lineup 2']))
    Doubles['Zip'] = Doubles.loc[:,'Zip'].apply(lambda x: sorted(x))
    Doubles['Zip'] = Doubles['Zip'].apply(set)
    Doubles['Zip'] = Doubles['Zip'].apply(tuple)
    Matchup = Doubles[Doubles['Zip'].map(len) > 1]
    Matchup = Matchup.drop_duplicates(subset=['Zip'])
    Matchup = Matchup.drop('Zip', axis=1)

    Matchup['Match Frequency'] = Matchup['WinP1'] + Matchup['WinP2']
    Matchup['Matchup Odds'] = Matchup['WinP1'].apply(str) + ' - ' +  Matchup['WinP2'].apply(str)
    matchup_df = Matchup[['Lineup 1','Lineup 2','Matchup Odds','Match Frequency']]
    matchup_df = matchup_df.sort_values('Match Frequency', ascending=False, ignore_index=True)
    print("Lineup Matchup View is ready")
    return matchup_df

def get_deck_and_class_view(master_df):
    # 2. Decks View

    # Sum up Decks based on archetypes
    decks = master_df.loc[:,'arc 1':'arc 2'].stack().value_counts(normalize = False, ascending = False)
    decks = decks.rename_axis("Deck Archetype").reset_index(name = 'Count')
    decks['Player %'] = (round((decks['Count']/(int(master_df.shape[0])))*100, 2))
    decks_df = decks.copy()

    # Sum up Decks based on class
    classes = master_df.loc[:,'class 1':'class 2'].stack().value_counts(normalize = False, ascending = False)
    classes = classes.rename_axis("Class").reset_index(name = 'Count')
    classes['Player %'] = (round((classes['Count']/(int(master_df.shape[0])))*100, 2))
    classes_df = classes.copy()

    print("Deck and Class View Dataset is ready")
    return(decks_df, classes_df)

def get_lineup_view(lineupdict, P1, P2, ResultP1, ResultP2):
    # 3. Lineup View
     
    lds = pd.DataFrame(lineupdict)
    lineup = lds["Lineup"].value_counts(normalize = False, ascending = False)
    lineup = lineup.rename_axis("Lineup").reset_index(name = 'Count')
    lineup['Player %'] = (round((lineup['Count']/(int(lds.shape[0])))*100, 2))
    lineup['Lineup'] = lineup.loc[:,'Lineup'].apply(lambda x: ' - '.join(x))

    Players = P1 + P2
    Wins = ResultP1 + ResultP2
    WinDS1 = pd.DataFrame([Players,Wins]).transpose().rename(columns={0:'profile', 1:'win'})
    WinDS = WinDS1.groupby('profile')['win'].sum().reset_index().sort_values('win', ascending=False)
    LineDS1 = WinDS.copy()
    LineDS1['profile'] = LineDS1.loc[:,'profile'].apply(lambda x: lineupdict['Lineup'][x])
    LineDS1['profile'] = LineDS1.loc[:,'profile'].apply(lambda x: ' - '.join(x))
    LineDS1 = LineDS1.rename(columns={'profile':'Lineup'})
    LineDS = LineDS1.groupby('Lineup')['win'].sum().reset_index().sort_values('win', ascending=False)

    total1 = pd.DataFrame(Players).rename(columns={0:'profile'}).dropna()
    total1['profile'] = total1.loc[:,'profile'].apply(lambda x: lineupdict['Lineup'][x])
    total1['profile'] = total1.loc[:,'profile'].apply(lambda x: ' - '.join(x))
    total1 = total1.rename(columns={'profile':'Lineup'})
    total = total1['Lineup'].value_counts(ascending = False).reset_index().rename(columns={'index':'Lineup', 'Lineup':'total'})

    LineupDS = pd.merge(LineDS, total, how='left')
    LineupDS['lose'] = LineupDS['total']-LineupDS['win']
    LineupDS['Winrate %'] = 100 * LineupDS['win']/LineupDS['total']
    LineupDS['Winrate %'] = LineupDS.loc[:,'Winrate %'].apply(lambda x:round(x, 2))

    LineupFinal = pd.merge(lineup, LineupDS, how='left')
    LineupFinal['Lineup'] = LineupFinal.loc[:,'Lineup'].apply(lambda x: x.split(" - "))
    LineupFinal[['Deck 1','Deck 2']] = pd.DataFrame(LineupFinal['Lineup'].to_list(), index=LineupFinal.index)
    LineupFinal_df = LineupFinal[['Deck 1', 'Deck 2', 'Count', 'Player %','win','lose','Winrate %']]

    print("Lineup View Dataset is ready")
    return LineupFinal_df

def get_top16_conversion_view(top16view_df, decks_df):
    #count deck and combine with data

    conv_top16 = top16view_df.copy()
    conv_top16['deck 1'] = conv_top16['deck 1'].apply(lambda x: Deck(x).archetype_checker())
    conv_top16['deck 2'] = conv_top16['deck 2'].apply(lambda x: Deck(x).archetype_checker())
    conv_decks = conv_top16.loc[:,'deck 1':'deck 2'].stack().value_counts(normalize = False, ascending = False)
    conv_decks = conv_decks.rename_axis("Deck Archetype").reset_index(name = 'Count')
    conv_decks['Top 16 Rep%'] = (round((conv_decks['Count']/(int(conv_top16.shape[0])))*100, 2))
    whole_decksdf = decks_df.copy()
    whole_decksdf = whole_decksdf.rename(columns={'Count':'Total', 'Player %':'Group Rep%'})
    mergedeck = conv_decks.merge(whole_decksdf)
    mergedeck['Conversion Rate %'] = round(mergedeck['Count']/mergedeck['Total'], 4)*100 
    mergedeck = mergedeck.rename(columns={'Count':'Top 16', 'Total':'Group'})
    mergedeck = mergedeck.astype(str)
    mergedeck['Conversion Rate %'] = mergedeck['Conversion Rate %'].astype(float)
    mergedeck['Top 16 (Player%)'] = mergedeck['Top 16'] + ' (' + mergedeck['Top 16 Rep%'] + '%)'
    mergedeck['Group (Player%)'] = mergedeck['Group'] + ' (' + mergedeck['Group Rep%'] + '%)'
    conv_page_df = mergedeck[['Deck Archetype','Top 16 (Player%)','Group (Player%)','Conversion Rate %']]
    
    print("Top 16 Conversion View Dataset is ready")
    return conv_page_df

### CrossCraft Deck Scraper
# tcode = 'el7lz6ffvNDk'
# entrieslink = 'https://sv.j-cg.com/competition/' + tcode + '/entries'
# source = requests.get(entrieslink).text
# soup = bs(source, 'lxml')
#     # Find and extract JSON file in HTML
# all_scripts = soup.find_all('script')
#     #currently hardcasted, faster processing but will be screwed when website changes
# dljson = all_scripts[7].string
#     #cleaning string to comply with JSON format
# cleanedjson = dljson[dljson.find('list'):dljson.find('listFiltered')]
# finaljson = cleanedjson.replace('list:','').strip()[:-1]
# data = json.loads(finaljson)
# jsondf = pd.DataFrame(data)

# sv = 'https://shadowverse-portal.com/deck_co/'
# jcg = 'https://sv.j-cg.com/user/'
# lang_eng = '?lang=en'
# data1 = jsondf.loc[jsondf['result']==1].copy()
# data1['d1'] = data1['sv_decks'].apply(lambda x: x[0]['hash'] if x else None)
# data1['d2'] = data1['sv_decks'].apply(lambda x: x[1]['hash'] if x else None)
# data1['deck 1']= data1['d1'].apply(lambda x: sv + x + lang_eng if x else 'Invalid Deck')
# data1['deck 2']= data1['d2'].apply(lambda x: sv + x + lang_eng if x else 'Invalid Deck')
# data1['profile']=data1['nicename'].apply(lambda x: jcg + x)
# data2 = data1[['profile','name','deck 1','deck 2']].copy()
# df = data2

# writer = pd.ExcelWriter("Excel_and_CSV/CrossCraft.xlsx", options={'strings_to_urls': True})
# df.to_excel(writer, 'MainData')
# writer.save()
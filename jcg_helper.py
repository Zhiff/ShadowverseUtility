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
    maxpage = 7
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

def group_winner_check_2(tcode):

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




tcode = 'E75bqtw8FqSS'
Top16 = group_winner_check_2(tcode)

# DeckA = ['a','a','c','b','a','c','a']
# DeckB = ['b','b','a','a','c','a','a']
# WinA = [1,1,0,1,1,0,1]
# WinB = [0,0,1,0,0,1,0]

# tab = {'DeckA': DeckA, 'DeckB': DeckB, 'WinA': WinA, 'WinB': WinB}
# df = pd.DataFrame(tab)
# df1 = df.groupby(['DeckA','DeckB'])['WinA'].sum().reset_index()
# df2 = df.groupby(['DeckA','DeckB'])['WinB'].sum().reset_index()
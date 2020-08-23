# -*- coding: utf-8 -*-
"""
Spyder Editor


This is the main file
"""
import pandas as pd
import excel_module as em
import website_scraper as ws
import stat_helper as sh
from deckmodule import Deck
import openpyxl as oxl
import requests
import numpy as np
from bs4 import BeautifulSoup as bs

# Excel Scraping, It will produce 3 excel files. FilteredDecks_View, FilteredDecks_Data, and Statistics and Breakdown
# Input : Excel sheet from SVO
# Requirements :    - all names and decklist must be inside 'Sheet1'
#                   - columns name , deck 1, deck 2, deck 3 must exists
#                   - decklists must end with ?lang=en or &lang=en


# ws.SVO_initial_scraper('Excel_and_CSV/SVO SEAO JULY Cup 2020 ez viewing copy.xlsx')



# Post SVO scraping, It will produce 2 excel files. FilteredDecks_View, and Post_SVO_Data
# Input : JSON hash from battlefy
# Requirements :    - SVO_Initial_Scraper must be ran, FilteredDecks_View contains all participants lineups
#                   - JSON hash must be valid
#                   - People changing name after tournament ended will skew the results

# bfy_tourneyhash = '5f02c761bf38ff0aa1f90bcf'
# bfy_stagehash = '5f37504d6ce6de28d63dd645'
# ws.SVO_posttourney_scraper(bfy_tourneyhash, bfy_stagehash)



# Other Website Scraping : JCG, MSCUP, It will produce 3 excel files. FilteredDecks_View, FilteredDecks_Data, and Statistics and Breakdown
# Input : Json page from respective website
# Requirements :    - JSON link must be valid



ws.JCG_scraper('https://sv.j-cg.com/compe/view/entrylist/2329/json')
# ws.manasurge_bfy_scraper('https://dtmwra1jsgyb0.cloudfront.net/tournaments/5f1e79e18e9cb60a9895e22d/teams')


# Shadowverse-utility
This is a personal Python based project related to Shadowverse competitive tournaments. The main purpose of this project is to extract information from SV competitive tournaments such as Shadowverse Open (SVO) , JCG Shadowverse, RAGE, and community tournaments. This project is purely a developer tool, so no UI are planned for this project. User can simply clone the entire repository and explore them with your preferred IDE. All functions can be called from Main.py file. Simply call your desired functions in order to satisfy your queries

Features :

- Shadowverse Portal Deck Analyzer
  - Given a svportallink, we can check numerous information within the deck
  - Following feature are implemented within Deck class
    - Archetype Checker
    - Class Checker
    - Deck Breakdown
    - Hash Generator
  - To use it, simply create a deck object and put svportal link as its parameter. Then call whichever method that suitable for your objective

- Tournament Statistics Generator

  - Main usage of this feature is to see the decks that all players bring in the tournaments and their compositions
  - Customized method for each tournaments SVO, JCG, Battlefy tournaments
  
  - SVO
    - Main Input is Excel document consisting player name and decks
    - Using SVO_initial_scraper method, informations such as Archetypes, Lineups, and Deck Breakdowns will be generated into excel files
    - Since the input is Excel, this method can be applied to anything that has decklist spreadsheets, not just limited to SVO
    - Further info such as Win/Lose/Ban stats can be scraped by puttting hashes of Battlefy page for that month SVO
    - Search matches based on player name is supported
    
  - JCG
    - Main input is JSON data directly from JCG website
    - Using JCG_scraper method, informations such as Archetypes, Lineups, and Deck Breakdowns will be generated into excel files
    - JCG_group_winner is an additional method to check actual group stages result since JCG rules allowed deck to be changed after group stages. 
    
  - Battlefy Tournaments
    - Main input is JSON data directly from battlefy
    - Currently only MS tournaments were customized
    - Using manasurge_bfy_scraper method, informations such as Archetypes, Lineups, and Deck Breakdowns will be generated into excel files
    
Contact me at Zhiff#6585 on discord if you have further question

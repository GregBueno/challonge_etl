'''
Author: Gregory Bueno
Email: gregorybueno@hotmail.com
Date: 26-10-2019
'''

import re
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pandas.io.json import json_normalize
from urllib.request import urlopen, Request

def parse_challonge(url):
    """
    Parameters
    ---
    url: Str
    
    Return
    ---
    Dataframe Strutured
    """
    
    # Tournament
    tournament = url.split('/')[-1]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = Request(url=url, headers=headers) 
    html = urlopen(req).read() 

    soup = BeautifulSoup(html, 'html.parser')
    info = soup.find("div",{"class":"details"})

    title_tour = info.find("div",{"class":"tournament-banner-header"})

    title_tour = title_tour.get_text().strip()

    detail_tour = info.find("ul",{"class":"meta inline-meta-list is-hidden-mobile"})

    detail_tour = detail_tour.find_all("div",{"class":"text"})

    detail_player = detail_tour[0].get_text().strip()
    detail_mode = detail_tour[1].get_text().strip()
    detail_date = detail_tour[2].get_text().strip()

    columns_tour = ['tournament','title_tournament','players_game','mode','date_start']
    df_tour = pd.DataFrame([[tournament,title_tour,detail_player,detail_mode,detail_date]],columns = columns_tour)

    df_tour['joincol'] = 1

    # Matches

    req = Request(url=url+'/module', headers=headers) 
    html = urlopen(req).read()

    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all("script")
    texthtml = scripts[7].get_text()

    pattern = r"(?<=\'TournamentStore\'] = )(.*)(?=; window)"
    pattern = r"(?<=\'TournamentStore\'] = )(.*)(?=; window._initialStoreState(.*)Theme)"

    result_text = re.findall(pattern,texthtml)

    json_result = result_text[0][0]

    dict_result = json.loads(json_result)

    df_list_matches = [ ]

    dict_matches = dict_result['matches_by_round']
    for key in dict_matches.keys():
        df_list_matches.append(json_normalize(dict_matches[key]) )

    df_match_final = pd.concat(df_list_matches).reset_index()
    df_match_final = df_match_final.drop('index',axis=1)

    columns = ['player1.id','player1.display_name','player2.id','player2.display_name','round','scores','state','tournament_id','id','winner_id','loser_id']

    df_match_final = df_match_final[[*columns]]

    df_match_final[['score1','score2']] = pd.DataFrame(df_match_final.scores.values.tolist(), index= df_match_final.index)

    df_match_final = df_match_final.drop('scores',axis=1)

    df_match_final['pts1'] = df_match_final['score1'].fillna(0)
    df_match_final['pts1'] = df_match_final['pts1'].astype(int)

    df_match_final['pts2'] = df_match_final['score2'].fillna(0)
    df_match_final['pts2'] = df_match_final['pts2'].astype(int)
    
    df_match_final['score1'] = df_match_final['pts1'] - df_match_final['pts2']
    df_match_final['score2'] = df_match_final['pts2'] - df_match_final['pts1']

    dfp1 = df_match_final[['player1.id','player1.display_name','round','state','tournament_id','id','winner_id','score1','pts1']]
    dfp2 = df_match_final[['player2.id','player2.display_name','round','state','tournament_id','id','winner_id','score2','pts2']]

    dfp1 = dfp1.rename(columns={'player1.id':'player_id','player1.display_name':'player_name','score1':'diff_score','id':'match_id','pts1':'total_score'})
    dfp1.loc[dfp1.player_id == dfp1.winner_id,'winner'] = True

    dfp2 = dfp2.rename(columns={'player2.id':'player_id','player2.display_name':'player_name','score2':'diff_score','id':'match_id','pts2':'total_score'})
    dfp2.loc[dfp2.player_id == dfp2.winner_id,'winner'] = True

    dfp = pd.concat([dfp1,dfp2])
    dfp = dfp.sort_values(by=['tournament_id','round','match_id']).reset_index()
    dfp = dfp.drop('index',axis=1)
    dfp = dfp.drop('winner_id',axis=1)

    dfp['winner'] = dfp['winner'].fillna(False)

    dfp['joincol'] = 1

    dfp = dfp.merge(df_tour,on=['joincol'],how='left')
    dfp = dfp.drop('joincol',axis=1)

    return dfp

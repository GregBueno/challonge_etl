# Challonge ETL

Simple parse of tournament create in challonge with Round Robin mode

This code can fetch tournament data created by others users

# Usage

## Single Tournament
```
import pandas as pd
from ChallongeETL import parse_challonge

url = "https://challonge.com/pt_BR/roit_garbage_out19"

df_data = parse_challonge(url)

df_data.head()
```

## Multiple Tournaments
```
import pandas as pd
from ChallongeETL import parse_challonge

list_url = ["https://challonge.com/pt_BR/roit_garbage_out19",
            "https://challonge.com/pt_BR/supreme_league_out19"]

df_list = []
for url in list_url:
    df_list.append(parse_challonge(url))
df_data = pd.concat(df_list)

df_data.head()
```

# Analysis
```
dfp_score = df_data.groupby(['player_name'])['score'].sum().reset_index()
dfp_wins = df_data.groupby(['player_name'])['winner'].sum().astype(int).reset_index()

dfp_res = pd.merge(dfp_score,dfp_wins,on=['player_name']).reset_index()
dfp_res = dfp_res.drop('index', axis=1)

dfp_res.sort_values(by=['winner','score'],ascending=False)
```

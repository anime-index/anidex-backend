from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

import pandas as pd

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

animes = pd.read_json('data/animes.json')
animes.sort_values('mal_score', ascending=False, inplace=True)

series = pd.read_json('data/series.json')
series['value'] = series.score.rank(ascending=False) + series.popularity.rank(ascending=False)
series.sort_values('value', inplace=True)
series['position'] = range(1, series.shape[0]+1)

SERIES_PER_PAGE = 30


@app.get('/')
def read_root():
    return {'Hello': 'World'}

@app.get('/top/anime')
def get_top_anime():
    return animes.fillna('').head(20).to_dict(orient='records')

@app.get('/top/series/{page}')
def get_top_series(page: int):
    lst = series[SERIES_PER_PAGE*page:SERIES_PER_PAGE*(page+1)].fillna(0).to_dict(orient='records')
    return {'page': page, 'last_page': (series.shape[0] - 1) // SERIES_PER_PAGE, 'lst': lst}

@app.get('/series/{item_id}')
def get_series(item_id: int):
    return series.loc[series.series_id==item_id].to_dict(orient='index')[item_id]

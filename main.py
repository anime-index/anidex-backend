from typing import Optional
from fastapi import FastAPI

import pandas as pd

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

animes = pd.read_json('data/animes.json')
series = pd.read_json('data/series.json')


@app.get('/')
def read_root(q: Optional[str] = None):
    return {'Hello': 'World'}

@app.get('/top/anime')
def get_top_anime():
    return animes.sort_values('mal_score', ascending=False).fillna('').head(20).to_dict(orient='records')

@app.get('/top/series')
def get_top_series():
    return series.sort_values('score', ascending=False).head(20).to_dict(orient='records')

@app.get('/series/{item_id}')
def get_franchise(item_id: int):
    return series.loc[series.series_id==item_id].to_dict(orient='index')[item_id]

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ITEMS_PER_PAGE = 30

animes = pd.read_json('data/animes_reduced.json')
series = pd.read_json('data/series.json')


@app.get('/')
def read_root():
    return {'Hello': 'World'}



from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


@app.get('/anime/search')
def searh_anime(page: int = 0, title='', type=''):
    filt_animes = animes.copy()
    filt_animes[['mal_score', 'episodes']] = filt_animes[['mal_score', 'episodes']].fillna(0)
    filt_animes['synopsis'] = filt_animes['synopsis'].fillna('No synopsis')
    if type:
        types = list(type.split(','))
        if 'Special' in types:
            types.extend(['Music', 'ONA', 'OVA', 'Special', 'Unknown'])
        filt_animes = animes[animes.type.isin(types)]

    tmp_animes = filt_animes[filt_animes.title.str.lower().str.contains(title.lower())]
    sorted_animes = tmp_animes.sort_values('mal_members', ascending=False)

    if sorted_animes.shape[0] == 0:
        tmp_animes = filt_animes
        tmp_animes['similarity'] = tmp_animes.title.str.lower().apply(lambda x: similar(x, title.lower()))
        tmp_animes['ran'] = tmp_animes.mal_members.rank()
        tmp_animes['comb'] = 0.5 * tmp_animes.similarity + 0.5 * tmp_animes.ran / tmp_animes.ran.max()
        sorted_animes = tmp_animes.sort_values('comb', ascending=False).head(90)

    lst = sorted_animes[ITEMS_PER_PAGE*page:ITEMS_PER_PAGE*(page+1)].to_dict(orient='records')
    return {'page': page, 'last_page': (sorted_animes.shape[0] - 1) // ITEMS_PER_PAGE, 'lst': lst}

@app.get('/top/anime')
def get_top_anime(page: int = 0, sort_by='mal_score,mal_members'):

    if sort_by == 'None':
        sorted_animes = tmp_animes.sample(animes.shape[0])
    
    else:
        tmp_animes = animes.copy()

        for item in sort_by.split(','):
            column = item.split('-r')[0]
            tmp_animes = tmp_animes[tmp_animes[column]!=0]
        
        tmp_animes['tmp'] = 0
        for item in sort_by.split(','):
            column = item.split('-r')[0]
            tmp_animes['tmp'] += tmp_animes[column].rank(ascending='-r' in item)
        
        sorted_animes = tmp_animes.sort_values('tmp')

    sorted_animes['position'] = range(1, sorted_animes.shape[0]+1)
    lst = sorted_animes[ITEMS_PER_PAGE*page:ITEMS_PER_PAGE*(page+1)].fillna(0).to_dict(orient='records')
    return {'page': page, 'last_page': (sorted_animes.shape[0] - 1) // ITEMS_PER_PAGE, 'lst': lst}


@app.get('/top/series')
def get_top_series(page: int = 0, sort_by='score,popularity'):

    if sort_by == 'None':
        sorted_series = series.sample(series.shape[0])
    
    else:
        tmp_series = series.copy()

        for item in sort_by.split(','):
            column = item.split('-r')[0]
            tmp_series = tmp_series[tmp_series[column]!=0]
        
        tmp_series['tmp'] = 0
        for item in sort_by.split(','):
            column = item.split('-r')[0]
            tmp_series['tmp'] += tmp_series[column].rank(ascending='-r' in item)
        
        sorted_series = tmp_series.sort_values('tmp')
    
    sorted_series['position'] = range(1, sorted_series.shape[0]+1)

    lst = sorted_series[ITEMS_PER_PAGE*page:ITEMS_PER_PAGE*(page+1)].dropna().to_dict(orient='records')
    return {'page': page, 'last_page': (sorted_series.shape[0] - 1) // ITEMS_PER_PAGE, 'lst': lst}


@app.get('/series/{series_id}')
def get_series(series_id: int):
    return series.loc[series_id].to_dict()

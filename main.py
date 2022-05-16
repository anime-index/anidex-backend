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


def select_genres(df, genres):
    for genre in genres:
        df = df[df.genres.astype('str').str.contains(genre)]
    return df


def select_types(df, types):
    if 'Special' in types:
        types.extend(['Music', 'ONA', 'OVA', 'Special', 'Unknown'])
    return df[df.type.isin(types)]


@app.get('/anime/search')
def searh_anime(page: int = 0, title='', genres='', types=''):

    tmp_animes = animes.copy()
    
    # Genre filtering
    if genres:
        tmp_animes = select_genres(tmp_animes, genres.split(','))

    # Type filtering
    if types:
        tmp_animes = select_types(tmp_animes, types.split(','))

    # Exact search + sort by popularity
    normal = tmp_animes[tmp_animes.title.str.lower().str.contains(title.lower())]
    sorted_animes = normal.sort_values('mal_members', ascending=False)

    # If no results then heuristic search + include popularity in results
    if sorted_animes.shape[0] == 0:
        tmp_animes['similarity'] = tmp_animes.title.str.lower().apply(lambda x: similar(x, title.lower()))
        tmp_animes['ran'] = tmp_animes.mal_members.rank()
        tmp_animes['comb'] = 0.75 * tmp_animes.similarity + 0.25 * tmp_animes.ran / tmp_animes.ran.max()
        sorted_animes = tmp_animes.sort_values('comb', ascending=False).head(90)

    lst = sorted_animes[ITEMS_PER_PAGE*page:ITEMS_PER_PAGE*(page+1)].to_dict(orient='records')
    return {'page': page, 'last_page': (sorted_animes.shape[0] - 1) // ITEMS_PER_PAGE, 'lst': lst}


@app.get('/top/anime')
def get_top_anime(page: int = 0, sort_by='mal_score,mal_members', genres='', types=''):

    tmp_animes = animes.copy()
    
    # Genre filtering
    if genres:
        tmp_animes = select_genres(tmp_animes, genres.split(','))

    # Type filtering
    if types:
        tmp_animes = select_types(tmp_animes, types.split(','))

    # Series sorting
    if sort_by == 'None':
        sorted_animes = tmp_animes.sample(tmp_animes.shape[0])
    
    else:

        # Drop columns with 0's in the search parameter
        for item in sort_by.split(','):
            column = item.split('-r')[0]
            tmp_animes = tmp_animes[tmp_animes[column]!=0]
        
        tmp_animes['tmp'] = 0
        for item in sort_by.split(','):
            column = item.split('-r')[0]
            tmp_animes['tmp'] += tmp_animes[column].rank(ascending='-r' in item)
        
        sorted_animes = tmp_animes.sort_values('tmp')

    # Numbering
    sorted_animes['position'] = range(1, sorted_animes.shape[0]+1)

    lst = sorted_animes[ITEMS_PER_PAGE*page:ITEMS_PER_PAGE*(page+1)].to_dict(orient='records')
    return {'page': page, 'last_page': (sorted_animes.shape[0] - 1) // ITEMS_PER_PAGE, 'lst': lst}


@app.get('/top/series')
def get_top_series(page: int = 0, sort_by='score,popularity', genres=''):

    tmp_series = series.copy()
    
    # Genre filtering
    if genres:
        tmp_series = select_genres(series, genres.split(','))

    # Series sorting
    if sort_by == 'None':
        sorted_series = tmp_series.sample(tmp_series.shape[0])
    
    else:

        # Drop columns with 0's in the search parameter
        for item in sort_by.split(','):
            column = item.split('-r')[0]
            tmp_series = tmp_series[tmp_series[column]!=0]
        
        tmp_series['tmp'] = 0
        for item in sort_by.split(','):
            column = item.split('-r')[0]
            tmp_series['tmp'] += tmp_series[column].rank(ascending='-r' in item)
        
        sorted_series = tmp_series.sort_values('tmp')
    
    # Numbering
    sorted_series['position'] = range(1, sorted_series.shape[0]+1)

    lst = sorted_series[ITEMS_PER_PAGE*page:ITEMS_PER_PAGE*(page+1)].to_dict(orient='records')
    return {'page': page, 'last_page': (sorted_series.shape[0] - 1) // ITEMS_PER_PAGE, 'lst': lst}


@app.get('/series/{series_id}')
def get_series(series_id: int):
    return series.loc[series_id].to_dict()

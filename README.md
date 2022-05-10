# anidex-backend

Backend REST api for the website, using Python's Fast API

Deployed on: [Anidex Deta](https://anidex.deta.dev/)

Data from: [kaggle @abhishtagatya](https://www.kaggle.com/datasets/abhishtagatya/my-anime-list-2021)

## Project setup (run on local)

### Get the code
```sh
git clone https://github.com/anime-index/anidex-backend
cd anidex-backend
```

### Install libraries
```sh
pip install -r requirements_local.txt
```

### Run the development server
```sh
uvicorn main:app
```

#### Ignore (deployment, database)
- MySQL cloud hosting

import os
import pickle
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
TMDB_API_TOKEN = os.getenv("TMDB_API_TOKEN")

if not TMDB_API_TOKEN:
    st.error('TMDB API token not found.')

@st.cache_data(ttl=3600)
def fetch_poster(movie_id):
    if not TMDB_API_TOKEN:
        return None

    url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}"

    headers = {
        "Authorization": f"Bearer {TMDB_API_TOKEN}",
        "accept": "application/json"
    }
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )
        # response.raise_for_status()
        if response.status_code != 200:
            print(
                f"TMDB error for movie ID {movie_id}: "
                f"{response.status_code} - {response.text[:200]}"
            )
            return None

        data = response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"

        return None

    except requests.exceptions.RequestException as error:
        print(f"TMDB API error for movie {movie_id}: {error}")
        return None


def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        # fetching poster from API
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies,recommended_movies_posters


movies_dict = pickle.load(open('movies_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl','rb'))

st.title('Movie Recommender System')
selected_movie_name = st.selectbox('How would you?',
                      movies['title'].values)

if st.button('Recommend'):
    names,posters = recommend(selected_movie_name)

    columns = st.columns(5)

    for column, name, poster in zip(columns, names, posters):
        with column:
            st.text(name)

            if poster:
                st.image(poster, use_container_width=True)
            else:
                st.caption("Poster unavailable")
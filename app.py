import streamlit as st
import pickle
import pandas as pd
import requests

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

API_KEY = "e448e3682d13c925da683590cd25cbe5"


# -------------------- FETCH MOVIE DETAILS --------------------
@st.cache_data(show_spinner=False)
def fetch_movie_details(title):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return "https://via.placeholder.com/500x750?text=Error", "N/A", "N/A"

        data = response.json()

        if not data.get('results'):
            return "https://via.placeholder.com/500x750?text=No+Poster", "N/A", "N/A"

        movie = data['results'][0]

        poster_path = movie.get('poster_path')
        rating = movie.get('vote_average', "N/A")
        release_date = movie.get('release_date', "N/A")

        poster_url = (
            f"https://image.tmdb.org/t/p/w500/{poster_path}"
            if poster_path
            else "https://via.placeholder.com/500x750?text=No+Poster"
        )

        year = release_date[:4] if release_date != "N/A" else "N/A"

        return poster_url, rating, year

    except Exception:
        return "https://via.placeholder.com/500x750?text=Error", "N/A", "N/A"


# -------------------- RECOMMEND FUNCTION --------------------
def recommend(movie):
    if movie not in movies['title'].values:
        return [], [], [], []

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    posters = []
    ratings = []
    dates = []

    for i in movies_list:
        title = movies.iloc[i[0]].title

        poster, rating, year = fetch_movie_details(title)

        recommended_movies.append(title)
        posters.append(poster)
        ratings.append(rating)
        dates.append(year)

    return recommended_movies, posters, ratings, dates


# -------------------- LOAD DATA --------------------
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))


# -------------------- UI --------------------
st.title('🎬 Movie Recommendation System')

selected_movie_name = st.selectbox(
    "Select a movie",
    movies['title'].values
)


# -------------------- BUTTON --------------------
if st.button('Recommend'):
    names, posters, ratings, dates = recommend(selected_movie_name)

    if len(names) == 0:
        st.error("Movie not found!")
    else:
        cols = st.columns(5)

        for i in range(5):
            with cols[i]:
                st.image(posters[i], use_container_width=True)
                st.markdown(f"**{names[i]}**")
                st.markdown(f"⭐ Rating: {ratings[i]}")
                st.markdown(f"📅 Year: {dates[i]}")
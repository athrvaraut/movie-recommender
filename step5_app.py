import streamlit as st
import pandas as pd
import requests

movie_similarity_df = pd.read_pickle('movie_similarity_small.pkl')
movies_list = sorted(movie_similarity_df.columns.tolist())

def recommend_movies(movie_name, n=5):
    if movie_name not in movie_similarity_df.columns:
        return []
    similar = movie_similarity_df[movie_name].sort_values(ascending=False)
    similar = similar.drop(movie_name)
    return similar.head(n).index.tolist()

def get_poster(movie_name):
    try:
        api_key = "8265bd1679663a7ea12ac168da84d2e8"
        name = movie_name.split("(")[0].strip()
        url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={name}"
        response = requests.get(url).json()
        if response['results']:
            poster_path = response['results'][0].get('poster_path','')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("Movie Recommender System")
st.markdown("### Find movies similar to your favourites!")

selected_movie = st.selectbox("Select a movie:", movies_list)

if st.button("Get Recommendations"):
    st.markdown("---")
    st.subheader(f"Movies similar to {selected_movie}")
    recommendations = recommend_movies(selected_movie, n=5)
    cols = st.columns(5)
    for i, movie in enumerate(recommendations):
        with cols[i]:
            poster = get_poster(movie)
            st.image(poster, use_column_width=True)
            st.caption(movie)
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="FlickFindr", page_icon="🎬", layout="wide")

st.markdown("""
<style>
#root > div:nth-child(1) > div > div > div > div > section > div {
    padding-top: 0rem;
}
header[data-testid="stHeader"] {
    display: none;
}
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
}
.main-title {
    text-align: center;
    font-size: 100px !important;
    font-weight: 900 !important;
    background: linear-gradient(90deg, #f7971e, #ffd200) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    padding: 40px 0 10px 0;
    letter-spacing: 6px;
    line-height: 1.1;
}
.subtitle {
    text-align: center;
    font-size: 24px !important;
    color: #cccccc !important;
    margin-bottom: 40px;
}
.movie-title {
    color: white !important;
    font-size: 12px;
    font-weight: 600;
    margin-top: 6px;
    text-align: center;
}
.rating {
    color: #ffd200 !important;
    font-size: 13px;
    text-align: center;
    margin-bottom: 8px;
}
.section-title {
    color: #ffd200 !important;
    font-size: 28px;
    font-weight: 700;
    margin: 40px 0 15px 0;
    border-left: 5px solid #ffd200;
    padding-left: 14px;
}
p, label, span {
    color: white !important;
}
div[data-testid="stSelectbox"] label p {
    font-size: 18px !important;
    color: white !important;
}
div[data-testid="stButton"] button {
    background: linear-gradient(90deg, #f7971e, #ffd200) !important;
    color: #000000 !important;
    font-weight: 800 !important;
    font-size: 18px !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 15px !important;
    width: 100%;
}
div[data-testid="stButton"] button:hover {
    background: linear-gradient(90deg, #ffd200, #f7971e) !important;
    color: #000000 !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.1) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 10px !important;
}
hr {
    border-color: rgba(255,255,255,0.15) !important;
}
</style>
""", unsafe_allow_html=True)

API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

movie_similarity_df = pd.read_pickle('movie_similarity_small.pkl')
movies_list = sorted(movie_similarity_df.columns.tolist())

def get_movie_details(title):
    try:
        name = title.split("(")[0].strip()
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={name}&include_adult=false&language=en-US&page=1"
        res = requests.get(url).json()
        if res['results']:
            movie = res['results'][0]
            poster = ""
            if movie.get('poster_path'):
                poster = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
            rating = movie.get('vote_average', 0)
            return poster, rating
    except:
        pass
    return "", 0

def get_trending_hollywood():
    try:
        url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}"
        res = requests.get(url).json()
        return res.get('results', [])[:8]
    except:
        return []

def get_trending_bollywood():
    try:
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_original_language=hi&sort_by=popularity.desc"
        res = requests.get(url).json()
        return res.get('results', [])[:8]
    except:
        return []

def recommend_movies(movie_name, n=5):
    if movie_name not in movie_similarity_df.columns:
        return []
    similar = movie_similarity_df[movie_name].sort_values(ascending=False)
    similar = similar.drop(movie_name)
    return similar.head(n).index.tolist()

def show_tmdb_card(movie, col):
    with col:
        poster = ""
        if movie.get('poster_path'):
            poster = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
        rating = movie.get('vote_average', 0)
        title = movie.get('title', '')[:22]
        if poster:
            st.image(poster, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/500x750?text=No+Poster", use_container_width=True)
        st.markdown(f"<p class='movie-title'>{title}</p>", unsafe_allow_html=True)
        if rating > 0:
            st.markdown(f"<p class='rating'>⭐ {rating:.1f}/10</p>", unsafe_allow_html=True)

def show_recommended_card(movie_name, col):
    with col:
        poster, rating = get_movie_details(movie_name)
        if poster:
            st.image(poster, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/500x750?text=No+Poster", use_container_width=True)
        short = movie_name[:22] + "..." if len(movie_name) > 22 else movie_name
        st.markdown(f"<p class='movie-title'>{short}</p>", unsafe_allow_html=True)
        if rating > 0:
            st.markdown(f"<p class='rating'>⭐ {rating:.1f}/10</p>", unsafe_allow_html=True)

st.markdown("<p class='main-title'>🎬 FlickFindr</p>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Discover movies you will love — Hollywood & Bollywood</p>", unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    selected_movie = st.selectbox("Search a movie to get recommendations:", movies_list)
    search_btn = st.button("🔍 Find Similar Movies", use_container_width=True)

if search_btn:
    st.markdown("<p class='section-title'>✨ Recommended For You</p>", unsafe_allow_html=True)
    recommendations = recommend_movies(selected_movie, n=5)
    if recommendations:
        cols = st.columns(5)
        for i, movie in enumerate(recommendations):
            show_recommended_card(movie, cols[i])
    else:
        st.warning("No recommendations found. Try another movie!")

st.markdown("<p class='section-title'>🔥 Trending This Week — Hollywood</p>", unsafe_allow_html=True)
hollywood = get_trending_hollywood()
if hollywood:
    cols = st.columns(8)
    for i, movie in enumerate(hollywood):
        show_tmdb_card(movie, cols[i])

st.markdown("<p class='section-title'>🎭 Trending This Week — Bollywood</p>", unsafe_allow_html=True)
bollywood = get_trending_bollywood()
if bollywood:
    cols = st.columns(8)
    for i, movie in enumerate(bollywood):
        show_tmdb_card(movie, cols[i])

st.markdown("---")
st.markdown("<p style='text-align:center;color:#666;font-size:13px;margin-top:10px;'>🎬 FlickFindr — Powered by MovieLens & TMDB API | Built for DWM PBL</p>", unsafe_allow_html=True)

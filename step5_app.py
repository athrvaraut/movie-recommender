import streamlit as st
import pandas as pd
import requests
import concurrent.futures
import json
import os
import bcrypt
from difflib import get_close_matches

st.set_page_config(page_title="FlickFindr", page_icon="🎬", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

def init_db():
    for f, default in [('users.json', {}), ('history.json', {}), ('users_extra.json', {})]:
        if not os.path.exists(f):
            with open(f, 'w') as fp:
                json.dump(default, fp)

def register_user(username, password, extra):
    with open('users.json', 'r') as f:
        users = json.load(f)
    if username in users:
        return False, "Username already exists!"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = hashed
    with open('users.json', 'w') as f:
        json.dump(users, f)
    with open('users_extra.json', 'r') as f:
        extras = json.load(f)
    extras[username] = extra
    with open('users_extra.json', 'w') as f:
        json.dump(extras, f)
    return True, "Registered successfully!"

def login_user(username, password):
    with open('users.json', 'r') as f:
        users = json.load(f)
    if username not in users:
        return False, "Username not found!"
    if bcrypt.checkpw(password.encode(), users[username].encode()):
        return True, "Login successful!"
    return False, "Wrong password!"

def save_history(username, movie, recs):
    with open('history.json', 'r') as f:
        history = json.load(f)
    if username not in history:
        history[username] = []
    history[username].insert(0, {"movie": movie, "recs": recs[:5]})
    history[username] = history[username][:20]
    with open('history.json', 'w') as f:
        json.dump(history, f)

def get_history(username):
    with open('history.json', 'r') as f:
        history = json.load(f)
    return history.get(username, [])

def get_user_extra(username):
    if os.path.exists('users_extra.json'):
        with open('users_extra.json', 'r') as f:
            extras = json.load(f)
        return extras.get(username, {})
    return {}

init_db()

st.markdown("""
<style>
header[data-testid="stHeader"] { display: none; }
.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
p, label, span, div { color: white; }
hr { border-color: rgba(255,255,255,0.1) !important; }
@keyframes float3d {
  0%   { transform: rotateX(15deg) rotateY(-5deg) translateY(0px); filter: drop-shadow(0 8px 16px rgba(255,210,0,0.4)); }
  50%  { transform: rotateX(10deg) rotateY(5deg) translateY(-10px); filter: drop-shadow(0 16px 24px rgba(255,210,0,0.6)); }
  100% { transform: rotateX(15deg) rotateY(-5deg) translateY(0px); filter: drop-shadow(0 8px 16px rgba(255,210,0,0.4)); }
}
.stat-box {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    border: 1px solid rgba(255,200,0,0.2);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    transition: transform 0.3s ease, border-color 0.3s ease;
}
.stat-box:hover { transform: translateY(-5px); border-color: rgba(255,200,0,0.6); }
.stat-num { font-size: 32px; font-weight: 900; color: #ffd200 !important; }
.stat-label { font-size: 13px; color: #aaaaaa !important; }
.section-title {
    color: #ffd200 !important;
    font-size: 24px;
    font-weight: 700;
    margin: 30px 0 15px 0;
    border-left: 5px solid #ffd200;
    padding-left: 14px;
}
.movie-title { color: white !important; font-size: 12px; font-weight: 600; margin-top: 6px; text-align: center; }
.rating { color: #ffd200 !important; font-size: 13px; text-align: center; }
.detail-box {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(255,200,0,0.2);
    margin: 16px 0;
}
div[data-testid="stButton"] button {
    background: linear-gradient(90deg, #f7971e, #ffd200) !important;
    color: #000000 !important;
    font-weight: 800 !important;
    font-size: 18px !important;
    border: none !important;
    border-radius: 10px !important;
}
div[data-baseweb="select"] > div {
    background: rgba(40,35,100,0.95) !important;
    border: 1px solid rgba(255,200,0,0.4) !important;
    border-radius: 10px !important;
}
div[data-baseweb="select"] span { color: white !important; }
li[role="option"] { background: #1a1640 !important; color: white !important; }
li[role="option"]:hover { background: #2d2870 !important; }
div[data-baseweb="base-input"] {
    background: rgba(40,35,100,0.95) !important;
    border: 1px solid rgba(255,200,0,0.4) !important;
    border-radius: 10px !important;
}
div[data-baseweb="base-input"] input { color: white !important; caret-color: white !important; background: transparent !important; }
input::placeholder { color: rgba(255,255,255,0.35) !important; }
.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid rgba(255,255,255,0.1) !important; }
.stTabs [data-baseweb="tab"] { color: #888888 !important; font-size: 15px !important; font-weight: 600 !important; background: transparent !important; }
.stTabs [aria-selected="true"] { color: #ffd200 !important; border-bottom: 3px solid #ffd200 !important; }
div[data-testid="stRadio"] label { color: white !important; font-size: 16px !important; }
div[data-testid="stExpander"] { background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,200,0,0.2) !important; border-radius: 12px !important; }
[data-testid="stPasswordInput"] svg { fill: white !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

API_KEY = "8265bd1679663a7ea12ac168da84d2e8"
movie_similarity_df = pd.read_pickle('movie_similarity_small.pkl')
movies_list = sorted(movie_similarity_df.columns.tolist())
svd_similarity_df = pd.read_pickle('svd_similarity.pkl')
bollywood_sim_df = pd.read_pickle('bollywood_similarity.pkl')
bollywood_df = pd.read_pickle('bollywood_df.pkl')
bollywood_list = sorted(bollywood_sim_df.columns.tolist())

@st.cache_data(ttl=3600)
def cached_poster(name):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={name}&language=en-US"
        res = requests.get(url, timeout=8).json()
        if res['results']:
            m = res['results'][0]
            poster = f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get('poster_path') else ""
            return poster, m.get('vote_average', 0)
    except:
        pass
    return "", 0

def recommend_movies(movie_name, n=8):
    if movie_name in svd_similarity_df.columns:
        similar = svd_similarity_df[movie_name].sort_values(ascending=False).drop(movie_name)
        return similar.head(n).index.tolist()
    elif movie_name in movie_similarity_df.columns:
        similar = movie_similarity_df[movie_name].sort_values(ascending=False).drop(movie_name)
        return similar.head(n).index.tolist()
    return []

def get_movie_details(title):
    try:
        name = title.split("(")[0].strip()
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={name}&language=en-US"
        res = requests.get(url, timeout=10).json()
        if res['results']:
            m = res['results'][0]
            movie_id = m['id']
            detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits"
            detail = requests.get(detail_url, timeout=10).json()
            poster = f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get('poster_path') else ""
            rating = m.get('vote_average', 0)
            overview = detail.get('overview', '')
            runtime = detail.get('runtime', 0)
            release = detail.get('release_date', '')[:4]
            genres = ', '.join([g['name'] for g in detail.get('genres', [])])
            cast = ', '.join([c['name'] for c in detail.get('credits', {}).get('cast', [])[:5]])
            director = ''
            for crew in detail.get('credits', {}).get('crew', []):
                if crew['job'] == 'Director':
                    director = crew['name']
                    break
            trailer_url = f"https://www.youtube.com/results?search_query={name}+official+trailer"
            imdb_url = f"https://www.imdb.com/find?q={name}&s=tt"
            return poster, rating, overview, runtime, release, genres, cast, director, trailer_url, imdb_url
    except:
        pass
    return "", 0, "", 0, "", "", "", "", "", ""

def get_poster_and_rating(title):
    name = title.split("(")[0].strip()
    return cached_poster(name)

def get_trending_hollywood():
    try:
        url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}&language=en-US"
        return requests.get(url, timeout=10).json().get('results', [])[:8]
    except:
        return []

def get_now_playing():
    try:
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={API_KEY}&language=en-US&region=US"
        return requests.get(url, timeout=10).json().get('results', [])[:8]
    except:
        return []

def get_trending_bollywood():
    try:
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_original_language=hi&sort_by=popularity.desc&vote_count.gte=100"
        return requests.get(url, timeout=10).json().get('results', [])[:8]
    except:
        return []

def get_latest_bollywood():
    try:
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_original_language=hi&sort_by=release_date.desc&vote_count.gte=20&primary_release_year=2024"
        return requests.get(url, timeout=10).json().get('results', [])[:8]
    except:
        return []

def fetch_bollywood_poster(r):
    name = r['movie_name']
    try:
        burl = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={name}&language=en-US"
        bres = requests.get(burl, timeout=4).json()
        hindi = [m for m in bres['results'] if m.get('original_language') in ['hi','ta','te']]
        found = hindi[0] if hindi else (bres['results'][0] if bres['results'] else None)
        poster = f"https://image.tmdb.org/t/p/w500{found['poster_path']}" if found and found.get('poster_path') else "https://via.placeholder.com/500x750?text=No+Poster"
    except:
        poster = "https://via.placeholder.com/500x750?text=No+Poster"
    return name, float(r.get('imdb_rating', 0)), poster

def show_movie_popup(movie_name):
    poster, rating, overview, runtime, release, genres, cast, director, trailer_url, imdb_url = get_movie_details(movie_name)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(poster if poster else "https://via.placeholder.com/500x750?text=No+Poster", use_container_width=True)
    with col2:
        st.markdown(f"<p style='color:#ffd200;font-size:26px;font-weight:800;margin:0;'>{movie_name}</p>", unsafe_allow_html=True)
        if rating > 0:
            st.markdown(f"<p style='color:#ffd200;font-size:20px;margin:6px 0;'>⭐ {rating:.1f}/10</p>", unsafe_allow_html=True)
        if release or runtime:
            st.markdown(f"<p style='color:#cccccc;font-size:14px;margin:4px 0;'>📅 {release} &nbsp;|&nbsp; ⏱️ {runtime} min</p>", unsafe_allow_html=True)
        if genres:
            st.markdown(f"<p style='color:#cccccc;font-size:14px;margin:4px 0;'>🎭 {genres}</p>", unsafe_allow_html=True)
        if director:
            st.markdown(f"<p style='color:#cccccc;font-size:14px;margin:4px 0;'>🎬 Director: <b style='color:white;'>{director}</b></p>", unsafe_allow_html=True)
        if cast:
            st.markdown(f"<p style='color:#cccccc;font-size:14px;margin:4px 0;'>🌟 Cast: <b style='color:white;'>{cast}</b></p>", unsafe_allow_html=True)
        if overview:
            st.markdown(f"<p style='color:#aaaaaa;font-size:13px;margin:12px 0;line-height:1.7;'>{overview[:350]}...</p>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='display:flex;gap:12px;margin-top:16px;flex-wrap:wrap;'>
            <a href='{trailer_url}' target='_blank' style='background:#ff0000;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:700;font-size:14px;'>▶ Watch Trailer</a>
            <a href='{imdb_url}' target='_blank' style='background:#f5c518;color:black;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:700;font-size:14px;'>🎬 IMDB Page</a>
        </div>
        """, unsafe_allow_html=True)

def show_tmdb_card(movie, col):
    with col:
        poster = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else "https://via.placeholder.com/500x750?text=No+Poster"
        rating = movie.get('vote_average', 0)
        title = movie.get('title', '')
        imdb_url = f"https://www.imdb.com/find?q={title}&s=tt"
        st.image(poster, use_container_width=True)
        st.markdown(f"<p class='movie-title'>{title[:20]}</p>", unsafe_allow_html=True)
        if rating > 0:
            st.markdown(f"<p class='rating'><a href='{imdb_url}' target='_blank' style='color:#ffd200;text-decoration:none;'>⭐ {rating:.1f}/10 ↗</a></p>", unsafe_allow_html=True)

def show_recommended_card(movie_name, col):
    with col:
        poster, rating = get_poster_and_rating(movie_name)
        imdb_url = f"https://www.imdb.com/find?q={movie_name}&s=tt"
        st.image(poster if poster else "https://via.placeholder.com/500x750?text=No+Poster", use_container_width=True)
        short = movie_name[:20] + "..." if len(movie_name) > 20 else movie_name
        st.markdown(f"<p class='movie-title'>{short}</p>", unsafe_allow_html=True)
        if rating > 0:
            st.markdown(f"<p class='rating'><a href='{imdb_url}' target='_blank' style='color:#ffd200;text-decoration:none;'>⭐ {rating:.1f}/10 ↗</a></p>", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; padding:50px 0 10px 0;'>
  <div style='display:inline-block; perspective:600px;'>
    <span style='font-size:90px;font-weight:900;font-family:Arial Black,sans-serif;letter-spacing:6px;background:linear-gradient(135deg,#ffd200 0%,#f7971e 40%,#ff6b6b 70%,#ffd200 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:float3d 4s ease-in-out infinite;display:block;'>🎬 FlickFindr</span>
  </div>
</div>
<div style='text-align:center;font-size:22px;color:#cccccc;margin:10px 0 20px 0;letter-spacing:1px;'>
Discover movies you will love — Hollywood & Bollywood
</div>
""", unsafe_allow_html=True)

if st.session_state.logged_in:
    st.markdown(f"<p style='text-align:right;color:#ffd200;font-size:14px;margin:-10px 0 10px 0;'>👤 {st.session_state.username}</p>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("<div class='stat-box'><p class='stat-num'>100K+</p><p class='stat-label'>Ratings Analysed</p></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='stat-box'><p class='stat-num'>9,700+</p><p class='stat-label'>Movies in Database</p></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='stat-box'><p class='stat-num'>450+</p><p class='stat-label'>Popular Movies Indexed</p></div>", unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["🔍  Find Movies", "📊  DWM Analysis", "👤  My Account", "ℹ️  About"])

with tab1:
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        search_type = st.radio("", ["🎬 Hollywood", "🎭 Bollywood"], horizontal=True)
        search_input = st.text_input("", placeholder="🔎  Type any movie name...")
        search_btn = st.button("🔍  Find Similar Movies", use_container_width=True)

    if search_btn and search_input:
        if search_type == "🎬 Hollywood":
            filtered = [m for m in movies_list if search_input.lower() in m.lower()]
            if not filtered:
                filtered = get_close_matches(search_input, movies_list, n=5, cutoff=0.4)
                if filtered:
                    st.info("Showing closest matches:")
            if filtered:
                st.markdown("<p class='section-title'>✨ Hollywood Recommendations</p>", unsafe_allow_html=True)
                recs = recommend_movies(filtered[0], n=8)
                if recs:
                    if st.session_state.logged_in:
                        save_history(st.session_state.username, filtered[0], recs)
                    cols = st.columns(8)
                    for i, movie in enumerate(recs):
                        show_recommended_card(movie, cols[i])
                    st.markdown("---")
                    st.markdown("<p style='color:#aaa;font-size:13px;margin-bottom:8px;'>🎬 Select any movie for full details, cast, trailer and IMDB:</p>", unsafe_allow_html=True)
                    selected_detail = st.selectbox("", ["Select a movie for details..."] + recs, label_visibility="collapsed")
                    if selected_detail and selected_detail != "Select a movie for details...":
                        with st.expander(f"📋 {selected_detail} — Full Details", expanded=True):
                            show_movie_popup(selected_detail)
                else:
                    st.warning("No recommendations found!")
            else:
                st.warning("Movie not found! Try: Toy Story, Matrix, Titanic, Forrest Gump, Inception")
        else:
            filtered = [m for m in bollywood_list if search_input.lower() in m.lower()]
            if not filtered:
                filtered = get_close_matches(search_input, bollywood_list, n=5, cutoff=0.3)
            if filtered:
                matched = filtered[0]
                st.markdown(f"<p class='section-title'>✨ Because you searched: {matched}</p>", unsafe_allow_html=True)
                row = bollywood_df[bollywood_df['movie_name'] == matched].iloc[0]
                imdb = row.get('imdb_rating', 0)
                verdict = row.get('verdict', '')
                genre = row.get('genre', '')
                actor = row.get('lead_actor', '')
                imdb_url = f"https://www.imdb.com/find?q={matched}&s=tt"
                st.markdown(f"""
                <div class='detail-box'>
                <p style='color:#ffd200;font-size:22px;font-weight:800;margin:0;'>{matched}</p>
                <p style='color:#cccccc;font-size:14px;margin:8px 0 0;'>
                <a href='{imdb_url}' target='_blank' style='color:#ffd200;text-decoration:none;'>⭐ IMDB: {imdb}/10 ↗</a>
                &nbsp;|&nbsp; 🎭 {genre} &nbsp;|&nbsp; 🎬 {actor} &nbsp;|&nbsp; 🏆 {verdict}
                </p>
                </div>
                """, unsafe_allow_html=True)
                similar = bollywood_sim_df[matched].sort_values(ascending=False).drop(matched)
                top_recs = similar.head(8).index.tolist()
                rec_rows = bollywood_df[bollywood_df['movie_name'].isin(top_recs)]
                rows_list = [r for _, r in rec_rows.iterrows()]
                if st.session_state.logged_in:
                    save_history(st.session_state.username, matched, top_recs)
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                    results = list(executor.map(fetch_bollywood_poster, rows_list))
                cols = st.columns(min(len(results), 8))
                for i, (name, rating, poster) in enumerate(results):
                    if i >= len(cols):
                        break
                    with cols[i]:
                        b_imdb_url = f"https://www.imdb.com/find?q={name}&s=tt"
                        st.image(poster, use_container_width=True)
                        short = name[:20] + "..." if len(name) > 20 else name
                        st.markdown(f"<p class='movie-title'>{short}</p>", unsafe_allow_html=True)
                        if rating > 0:
                            st.markdown(f"<p class='rating'><a href='{b_imdb_url}' target='_blank' style='color:#ffd200;text-decoration:none;'>⭐ {rating}/10 ↗</a></p>", unsafe_allow_html=True)
            else:
                st.warning("Not found! Try: Pathaan, KGF, 3 Idiots, Dangal, Stree, Animal, 12th Fail")
                st.info(f"Available: {', '.join(bollywood_list[:10])}...")

    st.markdown("<p class='section-title'>🔥 Trending Hollywood This Week</p>", unsafe_allow_html=True)
    hollywood = get_trending_hollywood()
    if hollywood:
        cols = st.columns(8)
        for i, m in enumerate(hollywood):
            show_tmdb_card(m, cols[i])

    st.markdown("<p class='section-title'>🎟️ Now Playing in Cinemas</p>", unsafe_allow_html=True)
    now = get_now_playing()
    if now:
        cols = st.columns(8)
        for i, m in enumerate(now):
            show_tmdb_card(m, cols[i])

    st.markdown("<p class='section-title'>🎭 Trending Bollywood</p>", unsafe_allow_html=True)
    bollywood_trend = get_trending_bollywood()
    if bollywood_trend:
        cols = st.columns(8)
        for i, m in enumerate(bollywood_trend):
            show_tmdb_card(m, cols[i])

    st.markdown("<p class='section-title'>🎬 Latest Bollywood 2024</p>", unsafe_allow_html=True)
    latest_b = get_latest_bollywood()
    if latest_b:
        cols = st.columns(8)
        for i, m in enumerate(latest_b):
            show_tmdb_card(m, cols[i])

with tab2:
    st.markdown("<p class='section-title'>📊 K-Means Clustering — Elbow Curve</p>", unsafe_allow_html=True)
    try:
        st.image('elbow_curve.png', use_container_width=True)
        st.caption("Elbow method — K=5 is the optimal number of user clusters")
    except:
        st.warning("elbow_curve.png not found in folder")
    st.markdown("<p class='section-title'>👥 User Clusters — PCA Visualization</p>", unsafe_allow_html=True)
    try:
        st.image('clusters_pca.png', use_container_width=True)
        st.caption("PCA reduces 9719 dimensions to 2D — 5 distinct user taste groups")
    except:
        st.warning("clusters_pca.png not found in folder")
    st.markdown("""
    <div style='background:rgba(255,255,255,0.04);backdrop-filter:blur(10px);padding:24px;border-radius:14px;border:1px solid rgba(255,200,0,0.2);margin-top:20px;'>
    <p style='color:#ffd200;font-size:17px;font-weight:700;margin-bottom:16px;'>DWM Pipeline</p>
    <p style='color:#cccccc;margin:8px 0;'>1️⃣ Load MovieLens 100K dataset</p>
    <p style='color:#cccccc;margin:8px 0;'>2️⃣ Merge, clean, remove nulls and duplicates</p>
    <p style='color:#cccccc;margin:8px 0;'>3️⃣ Build user-movie matrix (610 x 9719)</p>
    <p style='color:#cccccc;margin:8px 0;'>4️⃣ Apply cosine similarity between all movies</p>
    <p style='color:#cccccc;margin:8px 0;'>4b️⃣ SVD Matrix Factorization — U, Σ, Vt decomposition for better accuracy</p>
    <p style='color:#cccccc;margin:8px 0;'>5️⃣ K-Means groups users into 5 taste profiles</p>
    <p style='color:#cccccc;margin:8px 0;'>6️⃣ PCA reduces dimensions for 2D visualization</p>
    <p style='color:#cccccc;margin:8px 0;'>7️⃣ Elbow method finds optimal K value</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style='background:rgba(255,255,255,0.04);backdrop-filter:blur(10px);padding:24px;border-radius:14px;border:1px solid rgba(255,200,0,0.2);margin-top:20px;'>
    <p style='color:#ffd200;font-size:17px;font-weight:700;margin-bottom:12px;'>SVD vs Cosine Similarity</p>
    <p style='color:#cccccc;margin:6px 0;'>📐 Cosine Similarity — measures angle between movie vectors · score ~0.57</p>
    <p style='color:#cccccc;margin:6px 0;'>🧠 SVD — latent factor decomposition · score ~0.80</p>
    <p style='color:#cccccc;margin:6px 0;'>✅ SVD finds hidden patterns between genres</p>
    <p style='color:#cccccc;margin:6px 0;'>✅ Same algorithm used by Netflix and Amazon</p>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.markdown("""
            <div style='text-align:center;margin-bottom:20px;'>
            <p style='color:#ffd200;font-size:28px;font-weight:900;margin:0;'>👤 My Account</p>
            <p style='color:#aaaaaa;font-size:14px;margin:8px 0 0;'>Login to save your search history</p>
            </div>
            """, unsafe_allow_html=True)
            auth_type = st.radio("", ["🔑 Login", "📝 Register"], horizontal=True, key="auth_radio")
            if auth_type == "🔑 Login":
                l_user = st.text_input("Username", key="login_user", placeholder="Enter your username")
                l_pass = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔑 Login to FlickFindr", use_container_width=True):
                    if l_user and l_pass:
                        success, msg = login_user(l_user, l_pass)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.username = l_user
                            st.success(f"Welcome back {l_user}!")
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please enter username and password!")
                st.markdown("<p style='color:#aaaaaa;font-size:13px;text-align:center;margin-top:10px;'>No account? Switch to Register above.</p>", unsafe_allow_html=True)
            else:
                r_name = st.text_input("Full Name", key="reg_name", placeholder="Enter your full name")
                r_user = st.text_input("Username", key="reg_user", placeholder="Choose a username")
                r_email = st.text_input("Email", key="reg_email", placeholder="Enter your email address")
                r_phone = st.text_input("Phone Number", key="reg_phone", placeholder="Enter your phone number")
                r_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="Min 6 characters")
                r_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2", placeholder="Re-enter your password")
                col_a, col_b = st.columns(2)
                with col_a:
                    r_age = st.selectbox("Age Group", ["Select...", "Under 18", "18-25", "26-35", "36-50", "50+"], key="reg_age")
                with col_b:
                    r_genre = st.selectbox("Favourite Genre", ["Select...", "Action", "Comedy", "Drama", "Horror", "Romance", "Thriller", "Sci-Fi", "Animation", "Documentary"], key="reg_genre")
                r_gender = st.radio("Gender", ["Male", "Female", "Other", "Prefer not to say"], horizontal=True, key="reg_gender")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📝 Create Account", use_container_width=True):
                    if not all([r_name, r_user, r_email, r_phone, r_pass, r_pass2]):
                        st.warning("Please fill all fields!")
                    elif r_age == "Select..." or r_genre == "Select...":
                        st.warning("Please select Age Group and Favourite Genre!")
                    elif len(r_pass) < 6:
                        st.error("Password must be at least 6 characters!")
                    elif r_pass != r_pass2:
                        st.error("Passwords do not match!")
                    elif "@" not in r_email:
                        st.error("Please enter a valid email!")
                    elif len(r_phone) < 10:
                        st.error("Please enter a valid phone number!")
                    else:
                        extra = {"full_name": r_name, "email": r_email, "phone": r_phone, "age": r_age, "genre": r_genre, "gender": r_gender}
                        success, msg = register_user(r_user, r_pass, extra)
                        if success:
                            st.success(f"Welcome {r_name}! Account created successfully. Please switch to Login!")
                            st.balloons()
                        else:
                            st.error(msg)
                st.markdown("<p style='color:#aaaaaa;font-size:13px;text-align:center;margin-top:10px;'>Already have an account? Switch to Login above.</p>", unsafe_allow_html=True)
    else:
        extra = get_user_extra(st.session_state.username)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"<p class='section-title'>👤 Welcome, {extra.get('full_name', st.session_state.username)}!</p>", unsafe_allow_html=True)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.rerun()
        if extra:
            st.markdown(f"""
            <div class='detail-box'>
            <p style='color:#ffd200;font-size:18px;font-weight:700;margin:0 0 12px;'>Profile Details</p>
            <p style='color:#cccccc;margin:6px 0;'>📧 Email: {extra.get('email','')}</p>
            <p style='color:#cccccc;margin:6px 0;'>📱 Phone: {extra.get('phone','')}</p>
            <p style='color:#cccccc;margin:6px 0;'>🎂 Age: {extra.get('age','')}</p>
            <p style='color:#cccccc;margin:6px 0;'>🎭 Favourite Genre: {extra.get('genre','')}</p>
            <p style='color:#cccccc;margin:6px 0;'>👤 Gender: {extra.get('gender','')}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<p class='section-title'>🕐 Your Search History</p>", unsafe_allow_html=True)
        history = get_history(st.session_state.username)
        if history:
            for item in history:
                recs_str = ', '.join(item.get('recs', []))
                st.markdown(f"""
                <div class='detail-box' style='margin-bottom:12px;'>
                <p style='color:#ffd200;font-weight:700;font-size:16px;margin:0;'>🔍 {item['movie']}</p>
                <p style='color:#aaaaaa;font-size:13px;margin:6px 0 0;'>Recommended: {recs_str}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='detail-box' style='text-align:center;'>
            <p style='color:#aaaaaa;font-size:16px;margin:0;'>No search history yet!</p>
            <p style='color:#555555;font-size:13px;margin:8px 0 0;'>Search for movies and your history will appear here.</p>
            </div>
            """, unsafe_allow_html=True)

with tab4:
    st.markdown("""
    <div style='background:rgba(255,255,255,0.04);backdrop-filter:blur(12px);padding:30px;border-radius:16px;border:1px solid rgba(255,200,0,0.2);max-width:680px;margin:auto;'>
    <p style='color:#ffd200;font-size:30px;font-weight:800;text-align:center;'>🎬 FlickFindr</p>
    <p style='color:#cccccc;text-align:center;font-size:15px;margin-bottom:20px;'>Data Mining based Movie Recommendation System</p>
    <p style='color:#ffd200;font-weight:700;margin:10px 0 4px;'>📦 Dataset</p>
    <p style='color:#cccccc;'>MovieLens 100K — 100,836 ratings · 610 users · 9,742 movies</p>
    <p style='color:#ffd200;font-weight:700;margin:10px 0 4px;'>🧠 Algorithms</p>
    <p style='color:#cccccc;'>SVD · Cosine Similarity · K-Means Clustering · PCA · Collaborative Filtering</p>
    <p style='color:#ffd200;font-weight:700;margin:10px 0 4px;'>📚 DWM Concepts</p>
    <p style='color:#cccccc;'>Data Preprocessing · ETL · Data Warehousing · Unsupervised Learning · Dimensionality Reduction · Matrix Factorization</p>
    <p style='color:#ffd200;font-weight:700;margin:10px 0 4px;'>🛠️ Tech Stack</p>
    <p style='color:#cccccc;'>Python · Pandas · Scikit-learn · SciPy · Bcrypt · Streamlit · TMDB API · GitHub</p>
    <p style='color:#555;text-align:center;font-size:12px;margin-top:20px;'>DWM PBL Project — 2026</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align:center;color:#555;font-size:12px;'>🎬 FlickFindr — Powered by MovieLens & TMDB API | DWM PBL 2026</p>", unsafe_allow_html=True)
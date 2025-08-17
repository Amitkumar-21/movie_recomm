import streamlit as st
import pandas as pd
import pickle
import requests
import gdown  # for Google Drive downloads
import os

st.set_page_config(page_title="🎬 Movie Recommender", page_icon="🎥", layout="wide")

# ---------------- Google Drive URLs -----------------
SIMILARITY_FILE_ID = "1S20xVJJsxkeXpVRc9bbXUVjEqsZltUuu"
MOVIES_FILE_ID = "1HzB4SqVoQtRYLcvrkj_ws_ldX8i2v2jj"

# Download .pkl files from Google Drive at runtime
if not os.path.exists("similarity.pkl"):
    gdown.download(f"https://drive.google.com/uc?id={SIMILARITY_FILE_ID}", "similarity.pkl", quiet=False)

if not os.path.exists("movies_dict.pkl"):
    gdown.download(f"https://drive.google.com/uc?id={MOVIES_FILE_ID}", "movies_dict.pkl", quiet=False)

# ---------------- Load Data -----------------
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl','rb'))

# ---------------- API Fetch -----------------
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=90a050b53deefe302fe0da4b3cf8f8f8&language=en-US"
    response = requests.get(url)
    data = response.json()
    poster_path = data.get("poster_path", "")
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else ""
    overview = data.get("overview", "No description available.")
    rating = data.get("vote_average", "N/A")
    return full_path, overview, rating

# ---------------- Recommender -----------------
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:7]

    recommendations = []
    for i in distances:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        poster, overview, rating = fetch_movie_details(movie_id)
        recommendations.append((title, poster, overview, rating))
    return recommendations

# ---------------- UI -----------------
st.markdown(
    """
    <style>
    .movie-card {
        padding: 15px;
        border-radius: 15px;
        background-color: #1e1e1e;
        color: white;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        transition: transform 0.3s;
    }
    .movie-card:hover {
        transform: scale(1.05);
        background-color: #2a2a2a;
    }
    img {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🎬 Movie Recommendation System")
st.write("Find movies similar to your favorite one!")

selected_movie_name = st.selectbox(
    '👉 Choose a movie:', movies['title'].values
)

if st.button('🔍 Recommend'):
    recommendations = recommend(selected_movie_name)

    cols = st.columns(3)  # 3 movies per row
    for idx, (title, poster, overview, rating) in enumerate(recommendations):
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="movie-card">
                    <h4>{title}</h4>
                    <img src="{poster}" width="200">
                    <p><b>⭐ Rating:</b> {rating}</p>
                    <p style="font-size:13px;">{overview[:150]}...</p>
                </div>
            """, unsafe_allow_html=True)

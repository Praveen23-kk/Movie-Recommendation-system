import streamlit as st
import pandas as pd
import requests
import pickle
import os

st.set_page_config(page_title="Movie Recommender", layout="wide")

# Safe loading to prevent pandas compatibility issues
try:
    with open('movie_data.pkl', 'rb') as file:
        movies, cosine_sim = pickle.load(file)
except ModuleNotFoundError as e:
    st.error("❌ Error loading the pickle file. Please ensure you have the correct version of pandas.")
    st.stop()
except Exception as e:
    st.error(f"❌ An unexpected error occurred: {e}")
    st.stop()

# TMDB API Key
TMDB_API_KEY = '7b995d3c6fd91a2284b4ad8cb390c7b8'  # Replace with your key

# Function to fetch movie posters
def fetch_poster(movie_id):
    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}'
        response = requests.get(url)
        data = response.json()
        poster_path = data.get('poster_path')
        if not poster_path:
            return "https://via.placeholder.com/150?text=No+Image"
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except:
        return "https://via.placeholder.com/150?text=Error"

# Recommend similar movies
def get_recommendations(title, cosine_sim=cosine_sim):
    if title not in movies['title'].values:
        return pd.DataFrame()
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id']].iloc[movie_indices]

# UI
st.title("🎬 Movie Recommendation System")
st.markdown("#### Select a movie to get top 10 recommendations based on similarity")

selected_movie = st.selectbox("Choose a movie:", sorted(movies['title'].unique()))

if st.button("🎥 Recommend"):
    recommendations = get_recommendations(selected_movie)

    if recommendations.empty:
        st.warning("No recommendations found. Please select a different movie.")
    else:
        st.markdown("### 🔝 Top 10 Recommended Movies:")
        for i in range(0, 10, 5):
            cols = st.columns(5)
            for col, j in zip(cols, range(i, i + 5)):
                if j < len(recommendations):
                    movie = recommendations.iloc[j]
                    with col:
                        st.image(fetch_poster(movie['movie_id']), use_column_width=True)
                        st.caption(movie['title'])

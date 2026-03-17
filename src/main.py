# app.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # access root folder
from config import TMDB_API_KEY
import streamlit as st
import pandas as pd
import pickle
import requests
from movie_helper import (
    search_movie, get_movie_details, get_movie_cast, 
    get_cast_details, get_recommended_posters
)

# ---------------- Streamlit Config ----------------
st.set_page_config(layout="wide", page_title="🎬 Movie Recommendation System")

# ---------------- Load CSS ----------------
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("../static/style.css")  # path relative to src/app.py

# ---------------- User Config ----------------
API_KEY = TMDB_API_KEY
data = pd.read_csv('../Data/processed/final_combined_movie_metadata.csv')
movie_titles = [""] + list(data['movie_title'])

# Load sentiment classifier & vectorizer
clf = pickle.load(open('../model/sentiment_classifier.pkl', 'rb'))
vectorizer = pickle.load(open('../model/sentiment_vectorizer.pkl', 'rb'))

# ---------------- Functions ----------------
def get_tmdb_reviews(api_key, movie_id, limit=None):
    """Fetch TMDB reviews and classify sentiment"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews"
    params = {"api_key": api_key, "language": "en-US", "page": 1}
    reviews_sentiment = {}

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data_json = res.json()

        # Check if "results" key exists
        results = data_json.get("results", [])
        for r in results:
            content = r.get("content", "").strip()
            if not content:
                continue
            pred = clf.predict(vectorizer.transform([content]))[0]
            reviews_sentiment[content] = "Good" if pred else "Bad"
            # Stop if we reached the limit
            if limit and len(reviews_sentiment) >= limit:
                break

        return reviews_sentiment

    except Exception as e:
        st.error(f"Error fetching reviews: {e}")
        return {}

# ---------------- Streamlit App ----------------
st.title("🎬 Movie Recommendation System")
selected_movie = st.selectbox("Select a Movie", movie_titles)

if selected_movie:
    # Placeholder for entire page content
    page_placeholder = st.empty()

    with st.spinner("Please Wait... Loading all movie information..."):
        # Fetch all data first
        movie = search_movie(API_KEY, selected_movie)
        if movie is None:
            page_placeholder.error("Movie not found in TMDB.")
        else:
            details = get_movie_details(API_KEY, movie['id'])
            cast = get_movie_cast(API_KEY, movie['id'])
            filtered = data[data['movie_title'].str.lower() == selected_movie.lower()]
            rec_titles = rec_posters = []
            if not filtered.empty:
                movie_idx = filtered.index[0]
                similarity_matrix = pd.read_pickle('../model/similarity_matrix.pkl')
                movie_scores = similarity_matrix[movie_idx]
                similar_idxs = movie_scores.argsort()[-11:-1]
                rec_titles = data.iloc[similar_idxs]['movie_title'].tolist()
                rec_posters = get_recommended_posters(API_KEY, rec_titles)
            reviews = get_tmdb_reviews(API_KEY, movie['id'], limit=5)

        # ---------------- All information loaded, now render ----------------
        with page_placeholder.container():
            # Movie Details
            st.markdown(f"<h2 style='text-align:center'>{details['title']}</h2>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 2])
            with col1:
                if details['poster']:
                    st.image(details['poster'], width=250)
            with col2:
                st.markdown(f"**Overview:** {details['overview']}")
                st.markdown(f"**Genres:** {details['genres']}")
                st.markdown(f"**Release Date:** {details['release_date']}")
                st.markdown(f"**Runtime:** {details['runtime']} min")
                st.markdown(f"**Status:** {details['status']}")
                st.markdown(f"**Rating:** {details['rating']} ({details['vote_count']} votes)")

            # ---------------- Cast Cards (grid, click name to expand) ----------------
            if cast:
                st.markdown("<h3>ACTORS & ACTRESSES</h3>", unsafe_allow_html=True)
                n = 4  # cast per row
                for i in range(0, len(cast), n):
                    cols = st.columns(n)
                    for j, col in enumerate(cols):
                        idx = i + j
                        if idx < len(cast):
                            member = cast[idx]
                            cast_details = get_cast_details(API_KEY, member['id'])
                            profile = cast_details.get('profile') or member.get('profile') or ""
                            with col:
                                header = f"{member['name']} - {member['character']}"
                                with st.expander(header):
                                    if profile:
                                        st.image(profile, width=200)
                                    st.markdown(f"**Birthday:** {cast_details.get('birthday','N/A')}")
                                    st.markdown(f"**Place:** {cast_details.get('place','N/A')}")
                                    st.markdown(f"**Bio:** {cast_details.get('bio','N/A')}")

            # ---------------- Recommended Movies 5 per row ----------------
            if rec_titles:
                st.markdown("<h3>RECOMMENDED MOVIES FOR YOU</h3>", unsafe_allow_html=True)
                n = 5
                for i in range(0, len(rec_titles), n):
                    cols = st.columns(n)
                    for j, col in enumerate(cols):
                        idx = i + j
                        if idx < len(rec_titles):
                            with col:
                                st.image(rec_posters[idx], width=150)
                                st.markdown(f"<h5 style='text-align:center'>{rec_titles[idx]}</h5>", unsafe_allow_html=True)

            # ---------------- Reviews ----------------
            if reviews:
                st.markdown("<h3>USER REVIEWS</h3>", unsafe_allow_html=True)
                review_html = "<table class='table-bordered' style='color:white; width:100%;'>"
                review_html += "<tr><th>Review</th><th>Status</th></tr>"
                for r, status in reviews.items():
                    emoji = "&#128515;" if status=="Good" else "&#128534;"
                    review_html += f"<tr><td>{r}</td><td>{status} {emoji}</td></tr>"
                review_html += "</table>"
                st.markdown(review_html, unsafe_allow_html=True)
            else:
                st.info("No reviews found for this movie.")
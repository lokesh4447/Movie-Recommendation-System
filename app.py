import streamlit as st
import pandas as pd
import pickle
import urllib.parse



import os
import requests
import pickle

FILE_NAME = "similarity.pkl"

# OneDrive direct download URL
ONEDRIVE_URL = "https://1drv.ms/u/c/e7d158c771329572/IQA6dW5wGS8_ToaL5HBX8gnrAeB5yMtrTreF29N9ukHXaRk?e=jxgxpC"

# Download file if not exists
if not os.path.exists(FILE_NAME):
    with requests.get(ONEDRIVE_URL, stream=True) as r:
        r.raise_for_status()
        with open(FILE_NAME, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"{FILE_NAME} downloaded successfully!")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="MovieFlix | Your Personal Cinema",
    page_icon="🎬",
    layout="wide"
)

# Now you can load similarity.pkl
with open(FILE_NAME, 'rb') as f:
    similarity = pickle.load(f)
# ---------------- LOAD CSS ----------------
def load_css():
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # Styling will be handled if file exists


load_css()

# ---------------- LOAD DATA ----------------
try:
    movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open("similarity.pkl", "rb"))
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ---------------- SESSION STATES ----------------
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None
if "recent_movies" not in st.session_state:
    st.session_state.recent_movies = []
if "my_list" not in st.session_state:
    st.session_state.my_list = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"


# ---------------- HELPER FUNCTIONS ----------------
def recommend(movie):
    try:
        movie_index = movies[movies["title"] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]

        recommended_movies = []
        for i in movies_list:
            recommended_movies.append(movies.iloc[i[0]].title)
        return recommended_movies
    except:
        return []


def get_youtube_url(movie_title):
    # Generates a search link for the movie trailer
    query = urllib.parse.quote(f"{movie_title} official trailer")
    return f"https://www.youtube.com/results?search_query={query}"


# ---------------- NAVIGATION BAR ----------------
st.markdown("""
    <div class="navbar">
        <span class="nav-logo">🎬 MOVIEFLIX</span>
    </div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_page = "Home"
        st.rerun()
with m2:
    if st.button("🎥 Browse", use_container_width=True):
        st.session_state.current_page = "Movies"
        st.rerun()
with m3:
    if st.button("⭐ Recommended", use_container_width=True):
        st.session_state.current_page = "Recommended"
        st.rerun()
with m4:
    if st.button("❤️ My List", use_container_width=True):
        st.session_state.current_page = "My List"
        st.rerun()

st.markdown("---")

# ---------------- HOME PAGE ----------------
if st.session_state.current_page == "Home":
    st.markdown("<h1 style='text-align: center; color: #1e293b;'>Find Your Next Favorite Movie</h1>",
                unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        selected = st.selectbox("Search for a movie you like:", movies["title"].values)
        if st.button("🎯 Get Recommendations", use_container_width=True):
            st.session_state.selected_movie = selected
            if selected not in st.session_state.recent_movies:
                st.session_state.recent_movies.insert(0, selected)
            st.session_state.current_page = "Recommended"
            st.rerun()

# ---------------- MOVIES PAGE (BROWSE) ----------------
elif st.session_state.current_page == "Movies":
    st.markdown("<h2 class='page-header'>🎥 All Movies</h2>", unsafe_allow_html=True)
    search_query = st.text_input("Filter by name...", placeholder="Type here...")

    display_df = movies[movies["title"].str.contains(search_query, case=False)] if search_query else movies

    cols = st.columns(4)
    for idx, movie in enumerate(display_df["title"].head(20)):
        with cols[idx % 4]:
            st.info(movie)
            if st.button("View Similar", key=f"br_{idx}"):
                st.session_state.selected_movie = movie
                st.session_state.current_page = "Recommended"
                st.rerun()

# ---------------- RECOMMENDED PAGE ----------------
elif st.session_state.current_page == "Recommended":
    if not st.session_state.selected_movie:
    st.markdown(
        "<p style='color: #e11d48; font-weight: 600;'>Go to Home and search for a movie first!</p>",
        unsafe_allow_html=True
    )
    # if not st.session_state.selected_movie:
    #     st.warning("Go to Home and search for a movie first!")
    else:
        st.markdown(
            f"<h2 style='color: #e11d48;'>Recommendations based on {st.session_state.selected_movie}</h2>",
            unsafe_allow_html=True)
        recs = recommend(st.session_state.selected_movie)

        for idx, r in enumerate(recs):
            c1, c2, c3 = st.columns([4, 2, 1])

            # RECURSIVE FEATURE: Clicking the movie title shows recommendations for THAT movie
            with c1:
                if st.button(f"🎬 {r}", key=f"rec_btn_{idx}", use_container_width=True):
                    st.session_state.selected_movie = r
                    st.rerun()

            # YOUTUBE LINK FEATURE
            with c2:
                yt_url = get_youtube_url(r)
                st.markdown(f"<a href='{yt_url}' target='_blank' class='yt-button'>📺 Watch Trailer</a>",
                            unsafe_allow_html=True)

            with c3:
                if st.button("➕", key=f"rec_page_{idx}"):
                    if r not in st.session_state.my_list:
                        st.session_state.my_list.append(r)
                        st.toast(f"Added {r}!")

# ---------------- MY LIST PAGE ----------------
elif st.session_state.current_page == "My List":
    st.markdown("<h2 class='page-header'>❤️ My List</h2>", unsafe_allow_html=True)
    if not st.session_state.my_list:
        st.write("Your list is empty.")
    else:
        for m in st.session_state.my_list:
            c1, c2, c3 = st.columns([4, 2, 1])
            c1.write(f"**{m}**")
            c2.markdown(f"[Watch Trailer]({get_youtube_url(m)})")
            if c3.button("🗑️", key=f"del_{m}"):
                st.session_state.my_list.remove(m)
                st.rerun()

# ---------------- FOOTER ----------------
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
    <div class="footer">
        <p>© 2026 MovieFlix AI Recommender | Built with Streamlit</p>
        <p style='font-size: 10px; color: #94a3b8;'>Designed for Professional Movie Discovery</p>
    </div>
""", unsafe_allow_html=True)

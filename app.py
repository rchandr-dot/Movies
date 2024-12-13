import pickle
import streamlit as st
import requests
import time


# Function to fetch movie poster with retry logic
def fetch_poster(movie_id, retries=3):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8aaac00e4a437009ed6aa16b518cad05&language=en-US"
    for attempt in range(retries):
        try:
            data = requests.get(url)
            data.raise_for_status()  # Raise an error for bad HTTP responses (4xx/5xx)
            data = data.json()
            poster_path = data['poster_path']
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(2)  # Wait for 2 seconds before retrying
            else:
                st.error(f"Failed to fetch poster for movie ID {movie_id}: {e}")
                return None


# Function to fetch movie backdrop with retry logic
def fetch_backdrop(movie_id, retries=3):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8aaac00e4a437009ed6aa16b518cad05&language=en-US"
    for attempt in range(retries):
        try:
            data = requests.get(url)
            data.raise_for_status()
            data = data.json()
            backdrop_path = data['backdrop_path']
            if backdrop_path:
                full_backdrop = "https://image.tmdb.org/t/p/original" + backdrop_path
                return full_backdrop
            else:
                return "https://www.example.com/default-background.jpg"  # Default background if no backdrop found
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retrying
            else:
                st.error(f"Failed to fetch backdrop for movie ID {movie_id}: {e}")
                return "https://www.example.com/default-background.jpg"  # Return default backdrop if fails


# Function to recommend movies (no changes here)
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_ids = []
    for i in distances[1:7]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_ids.append(movie_id)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_ids


# Load the movie data and similarity matrix
movies = pickle.load(open('model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

# Default background image URL (before movie is selected)
default_background_url = "https://www.example.com/default-background.jpg"

# Set the default background
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url('{default_background_url}');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stHeader, .stSubHeader, .stText {{
        color: white;  /* Change text color to white */
    }}
    .recommended-movie-title {{
        font-size: 18px;
        font-weight: bold;
        color: #FFFFFF;  /* White text for movie titles */
        text-decoration: none;
        padding: 10px;
        background-color: rgba(0, 0, 0, 0.6);  /* Light black background for movie title */
        border-radius: 5px;
        transition: all 0.3s ease-in-out;
    }}
    .recommended-movie-title:hover {{
        color: #FF6347;  /* Change color on hover (Tomato red) */
        transform: scale(1.1);  /* Enlarge title */
    }}
    .recommended-movie-poster {{
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: all 0.3s ease-in-out;
    }}
    .recommended-movie-poster:hover {{
        transform: scale(1.1);  /* Enlarge poster */
    }}
    .recommended-movie-box {{
        display: inline-block;
        margin: 10px;
        text-align: center;
    }}
    .movie-dropdown, .stTextInput, .stSelectbox {{
        background-color: rgba(0, 0, 0, 0.5);  /* Light background to ensure text visibility */
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Page Header
st.header('Movie Recommender System')

# Display a placeholder message above the dropdown
st.markdown("### Type a movie or select a movie from the dropdown below:")

# Movie selection dropdown with an empty string as the first item
movie_list = [""] + list(movies['title'].values)  # Add an empty string at the start for no default selection
selected_movie = st.selectbox(
    "Select a movie:",
    movie_list,
    key="movie_dropdown",
)

# Fetch backdrop for the selected movie and set it as the background
if selected_movie:
    selected_movie_id = movies[movies['title'] == selected_movie].iloc[0]['movie_id']
    background_image_url = fetch_backdrop(selected_movie_id)

    # Dynamically set the background image CSS
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url('{background_image_url}');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .stHeader, .stSubHeader, .stText {{
            color: white;  /* Ensure text is white */
        }}
        .recommended-movie-title {{
            font-size: 18px;
            font-weight: bold;
            color: #FFFFFF;  /* White text for movie titles */
            text-decoration: none;
            padding: 10px;
            background-color: rgba(0, 0, 0, 0.6);  /* Light background for movie title */
            border-radius: 5px;
            transition: all 0.3s ease-in-out;
        }}
        .recommended-movie-title:hover {{
            color: #FF6347;  /* Change color on hover (Tomato red) */
            transform: scale(1.1);  /* Enlarge title */
        }}
        .recommended-movie-poster {{
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: all 0.3s ease-in-out;
        }}
        .recommended-movie-poster:hover {{
            transform: scale(1.1);  /* Enlarge poster */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Button to show recommendations
    if st.button('Show Recommendation'):
        recommended_movie_names, recommended_movie_posters, recommended_movie_ids = recommend(selected_movie)

        # Number of columns per row
        cols_per_row = 3
        for i in range(0, len(recommended_movie_names), cols_per_row):
            cols = st.columns(cols_per_row)  # Create a row with the specified number of columns
            for j, col in enumerate(cols):
                if i + j < len(recommended_movie_names):
                    col.markdown(
                        f'''
                        <div class="recommended-movie-box">
                            <a class="recommended-movie-title" href="https://www.themoviedb.org/movie/{recommended_movie_ids[i + j]}" target="_blank">
                                {recommended_movie_names[i + j]}
                            </a>
                            <a href="https://www.themoviedb.org/movie/{recommended_movie_ids[i + j]}" target="_blank">
                                <img class="recommended-movie-poster" src="{recommended_movie_posters[i + j]}" width="150">
                            </a>
                        </div>
                        ''',
                        unsafe_allow_html=True
                    )

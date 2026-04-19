# Netflix Recommendation System

A Streamlit-based movie recommendation app that combines:
- **content-based recommendations** (precomputed similarity matrix), and
- **review sentiment tagging** (pretrained sentiment model),

while enriching results with live movie, cast, poster, and review data from **TMDB API**.

## Features

- Search/select a movie from processed metadata.
- Display movie details (overview, genres, release date, runtime, rating, poster).
- Show top cast with expandable profiles.
- Recommend similar movies using a saved similarity matrix.
- Fetch TMDB user reviews and classify each review as **Good** or **Bad**.

## Project Structure

```text
Netflix_Recommendation_System/
├── Data/
│   ├── raw/                     # raw movie/review sources
│   └── processed/               # cleaned/final metadata used by app
├── model/
│   ├── similarity_matrix.pkl
│   ├── sentiment_classifier.pkl
│   ├── sentiment_vectorizer.pkl
│   └── tfidf_vectorizer.pkl
├── notebooks/                   # data prep + model experimentation
├── src/
│   ├── main.py                  # Streamlit application entrypoint
│   └── movie_helper.py          # TMDB helper functions
├── static/
│   └── style.css                # app styling
└── README.md
```

## Requirements

- Python 3.9+ (recommended)
- A TMDB API key: https://www.themoviedb.org/settings/api

Python packages used by the app:
- `streamlit`
- `pandas`
- `requests`

> The app also loads local `.pkl` model artifacts from the `model/` directory.

## Setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install streamlit pandas requests
```

Create `config.py` in the repository root:

```python
TMDB_API_KEY = "your_tmdb_api_key_here"
```

For safety, ensure `config.py` is ignored by Git (for example, add `config.py` to `.gitignore`) so API keys are not committed.

## Run the App

`src/main.py` uses relative paths, so run Streamlit **from the `src/` directory**:

```bash
cd src
streamlit run main.py
```

Then open the local Streamlit URL shown in terminal (usually `http://localhost:8501`).

## Data & Model Artifacts Used at Runtime

- `Data/processed/final_combined_movie_metadata.csv`
- `model/similarity_matrix.pkl`
- `model/sentiment_classifier.pkl`
- `model/sentiment_vectorizer.pkl`

If any of these files are missing, recommendations/review sentiment parts of the app will fail.

## Notes

- API calls depend on TMDB availability and key limits.
- Movie matching currently uses the first TMDB search result.
- Recommendation quality depends on the preprocessed metadata and saved similarity matrix.

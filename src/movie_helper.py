# movie_helper.py
import requests

TMDB_BASE = "https://api.themoviedb.org/3"

def search_movie(api_key, title):
    """Search movie by title and return first result"""
    url = f"{TMDB_BASE}/search/movie"
    params = {"api_key": api_key, "query": title}
    res = requests.get(url, params=params)
    res.raise_for_status()
    data = res.json()
    if data['results']:
        return data['results'][0]  # Return first match
    return None

def get_movie_details(api_key, movie_id):
    """Get full movie details"""
    url = f"{TMDB_BASE}/movie/{movie_id}"
    params = {"api_key": api_key}
    res = requests.get(url, params=params)
    res.raise_for_status()
    data = res.json()
    # Format runtime
    runtime = data.get("runtime", 0)
    hours = runtime // 60
    minutes = runtime % 60
    runtime_str = f"{hours} hour(s) {minutes} min(s)" if minutes else f"{hours} hour(s)"
    # Genres as comma-separated string
    genres = ", ".join([g['name'] for g in data.get("genres", [])])
    poster = f"https://image.tmdb.org/t/p/original{data.get('poster_path')}" if data.get('poster_path') else None

    return {
        "title": data.get("original_title"),
        "imdb_id": data.get("imdb_id"),
        "overview": data.get("overview"),
        "genres": genres,
        "rating": data.get("vote_average"),
        "vote_count": data.get("vote_count"),
        "release_date": data.get("release_date"),
        "runtime": runtime_str,
        "status": data.get("status"),
        "poster": poster
    }

def get_movie_cast(api_key, movie_id, top_n=10):
    """Get top cast of the movie"""
    url = f"{TMDB_BASE}/movie/{movie_id}/credits"
    params = {"api_key": api_key}
    res = requests.get(url, params=params)
    res.raise_for_status()
    data = res.json()
    cast_list = []
    for c in data.get("cast", [])[:top_n]:
        profile = f"https://image.tmdb.org/t/p/original{c['profile_path']}" if c.get('profile_path') else None
        cast_list.append({
            "id": c['id'],
            "name": c['name'],
            "character": c['character'],
            "profile": profile
        })
    return cast_list

def get_cast_details(api_key, cast_id):
    """Get birthday, bio, and place of birth of a cast member"""
    url = f"{TMDB_BASE}/person/{cast_id}"
    params = {"api_key": api_key}
    res = requests.get(url, params=params)
    res.raise_for_status()
    data = res.json()
    birthday = data.get("birthday")
    bio = data.get("biography")
    place = data.get("place_of_birth")
    return {"birthday": birthday, "bio": bio, "place": place}

def get_recommended_posters(api_key, movie_titles):
    """Get posters for list of movie titles"""
    posters = []
    for title in movie_titles:
        movie = search_movie(api_key, title)
        if movie and movie.get("poster_path"):
            posters.append(f"https://image.tmdb.org/t/p/original{movie['poster_path']}")
        else:
            posters.append(None)
    return posters
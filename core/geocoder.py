# Maps subreddit names and keywords to lat/lon coordinates

SUBREDDIT_LOCATIONS = {
    "london": (51.5074, -0.1278),
    "tokyo": (35.6762, 139.6503),
    "nyc": (40.7128, -74.0060),
    "losangeles": (34.0522, -118.2437),
    "india": (20.5937, 78.9629),
    "canada": (56.1304, -106.3468),
    "australia": (25.2744, 133.7751),
    "europe": (54.5260, 15.2551),
    "worldnews": (0.0, 0.0),      # global
    "news": (0.0, 0.0),
    "gaming": (0.0, 0.0),
}

KEYWORD_LOCATIONS = {
    "tokyo": (35.6762, 139.6503),
    "paris": (48.8566, 2.3522),
    "dubai": (25.2048, 55.2708),
    "berlin": (52.5200, 13.4050),
    "moscow": (55.7558, 37.6173),
    "beijing": (39.9042, 116.4074),
}

DEFAULT_LOCATION = (0.0, 0.0)   # fallback for unknown

def geocode_subreddit(subreddit_name: str) -> tuple:
    key = subreddit_name.lower().replace("r/", "")
    return SUBREDDIT_LOCATIONS.get(key, DEFAULT_LOCATION)

def geocode_keyword(text: str) -> tuple:
    text_lower = text.lower()
    for keyword, coords in KEYWORD_LOCATIONS.items():
        if keyword in text_lower:
            return coords
    return DEFAULT_LOCATION
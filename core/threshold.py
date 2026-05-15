# Conditions that must be met for raw data to become a Heat Event

THRESHOLDS = {
    "reddit_comments_per_min": 200,     # comments/min to trigger
    "reddit_upvotes_per_min": 1000,
    "youtube_concurrent_viewers": 100000,
    "twitch_viewers": 50000,
    "meme_mention_count": 500,          # mentions in 10 min window
}

def is_heat_event(event_type: str, velocity: int) -> bool:
    threshold = THRESHOLDS.get(event_type)
    if threshold is None:
        return False
    return velocity >= threshold

def get_intensity(velocity: int, max_velocity: int = 10000) -> float:
    """Normalize velocity to 0.0 - 1.0 intensity."""
    return min(velocity / max_velocity, 1.0)

def get_phase(age_seconds: int) -> str:
    """Return decay phase based on event age."""
    if age_seconds <= 30:
        return "ping"
    elif age_seconds <= 300:    # 5 min
        return "glow"
    elif age_seconds <= 1800:   # 30 min
        return "cool"
    else:
        return "ambient"
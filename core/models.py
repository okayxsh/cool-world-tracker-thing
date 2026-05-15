from pydantic import BaseModel
from typing import Literal

class HeatEvent(BaseModel):
    id: str
    type: Literal["reddit_spike", "youtube_live", "twitch_game", "meme"]
    lat: float
    lon: float
    intensity: float        # 0.0 - 1.0
    sentiment: Literal["positive", "neutral", "controversial", "chaos", "hype"]
    title: str
    velocity: int
    phase: Literal["ping", "glow", "cool", "ambient"]

class Batch(BaseModel):
    timestamp: int
    batch_id: str
    events: list[HeatEvent]
    global_sentiment: str
    bpm: int
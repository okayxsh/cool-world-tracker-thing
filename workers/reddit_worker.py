import asyncio
import asyncpraw
import os
import time
import uuid
from dotenv import load_dotenv
from core.models import HeatEvent
from core.geocoder import geocode_subreddit, geocode_keyword
from core.sentiment import analyze
from core.threshold import is_heat_event, get_intensity, get_phase
from redis_client import redis_client
import json

load_dotenv()

SUBREDDITS = [
    "all", "gaming", "news", "worldnews",
    "technology", "movies", "london", "india",
    "anime", "sports"
]

async def start():
    reddit = asyncpraw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "netpulse/1.0")
    )

    print("[Reddit Worker] Started")

    while True:
        try:
            for sub_name in SUBREDDITS:
                subreddit = await reddit.subreddit(sub_name)
                async for post in subreddit.hot(limit=10):
                    await process_post(post)
            await asyncio.sleep(10)  # poll every 10 seconds
        except Exception as e:
            print(f"[Reddit Worker] Error: {e}")
            await asyncio.sleep(15)

async def process_post(post):
    try:
        # estimate velocity from score and comments
        velocity = post.num_comments + (post.score // 10)

        if not is_heat_event("reddit_comments_per_min", velocity):
            return

        lat, lon = geocode_subreddit(post.subreddit.display_name)
        if lat == 0.0 and lon == 0.0:
            lat, lon = geocode_keyword(post.title)

        sentiment = analyze(post.title)
        age = int(time.time()) - post.created_utc
        phase = get_phase(int(age))
        intensity = get_intensity(velocity)

        event = HeatEvent(
            id=f"reddit_{post.id}",
            type="reddit_spike",
            lat=lat,
            lon=lon,
            intensity=intensity,
            sentiment=sentiment,
            title=f"r/{post.subreddit.display_name} — {post.title[:80]}",
            velocity=velocity,
            phase=phase
        )

        # store in Redis sorted set by timestamp
        await redis_client.zadd(
            "events",
            {event.model_dump_json(): int(time.time())}
        )
        await redis_client.set(f"event:{event.id}", event.model_dump_json())
        print(f"[Reddit] Heat Event: {event.title}")

    except Exception as e:
        print(f"[Reddit Worker] process_post error: {e}")
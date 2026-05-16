import asyncio
import os
import time
import json
from collections import defaultdict
from dotenv import load_dotenv
import tweepy
from core.models import HeatEvent
from core.geocoder import geocode_keyword
from core.sentiment import analyze
from core.threshold import is_heat_event, get_intensity, get_phase
from redis_client import redis_client

load_dotenv()

async def start():
    # Twitter free tier is very limited
    # this worker will gracefully skip if no API key is set
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        print("[Twitter Worker] No bearer token set, skipping.")
        return

    client = tweepy.Client(bearer_token=bearer_token)
    print("[Twitter Worker] Started")

    while True:
        try:
            # fetch trending topics by searching recent hot keywords
            queries = ["trending", "breaking", "viral", "leaked", "announcement"]
            keyword_counts = defaultdict(int)

            for query in queries:
                response = client.search_recent_tweets(
                    query=f"{query} -is:retweet lang:en",
                    max_results=100,
                    tweet_fields=["text", "created_at"]
                )

                if not response.data:
                    continue

                for tweet in response.data:
                    words = tweet.text.lower().split()
                    for word in words:
                        if word.startswith("#") and len(word) > 3:
                            keyword_counts[word] += 1

            # find keywords that crossed meme threshold
            for keyword, count in keyword_counts.items():
                if not is_heat_event("meme_mention_count", count):
                    continue

                lat, lon = geocode_keyword(keyword)
                sentiment = analyze(keyword)
                intensity = get_intensity(count, max_velocity=1000)
                phase = get_phase(0)

                event = HeatEvent(
                    id=f"twitter_{keyword}_{int(time.time())}",
                    type="meme",
                    lat=lat,
                    lon=lon,
                    intensity=intensity,
                    sentiment=sentiment,
                    title=f"Twitter/X — {keyword} trending ({count} mentions)",
                    velocity=count,
                    phase=phase
                )

                await redis_client.zadd(
                    "events",
                    {event.model_dump_json(): int(time.time())}
                )
                await redis_client.set(f"event:{event.id}", event.model_dump_json())
                print(f"[Twitter] Meme Event: {event.title}")

            await asyncio.sleep(20)

        except Exception as e:
            print(f"[Twitter Worker] Error: {e}")
            await asyncio.sleep(30)
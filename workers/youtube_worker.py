import asyncio
import os
import time
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from core.models import HeatEvent
from core.geocoder import geocode_keyword
from core.sentiment import analyze
from core.threshold import is_heat_event, get_intensity, get_phase
from redis_client import redis_client

load_dotenv()

# Known creator locations
CREATOR_LOCATIONS = {
    "kai cenat": (40.7128, -74.0060),       # NYC
    "mrbeast": (35.7796, -78.6382),         # North Carolina
    "pewdiepie": (51.5074, -0.1278),        # London
    "ishowspeed": (39.9612, -82.9988),      # Columbus Ohio
}

async def start():
    youtube = build(
        "youtube", "v3",
        developerKey=os.getenv("YOUTUBE_API_KEY"),
        static_discovery = False
    )

    print("[YouTube Worker] Started")

    while True:
        try:
            # search for live streams
            search_response = youtube.search().list(
                part="snippet",
                eventType="live",
                type="video",
                order="viewCount",
                maxResults=10
            ).execute()

            video_ids = [
                item["id"]["videoId"]
                for item in search_response.get("items", [])
            ]

            if not video_ids:
                await asyncio.sleep(30)
                continue

            # get live viewer counts
            stats_response = youtube.videos().list(
                part="liveStreamingDetails,snippet",
                id=",".join(video_ids)
            ).execute()

            for item in stats_response.get("items", []):
                live_details = item.get("liveStreamingDetails", {})
                concurrent = int(
                    live_details.get("concurrentViewers", 0)
                )

                if not is_heat_event("youtube_concurrent_viewers", concurrent):
                    continue

                title = item["snippet"]["title"]
                channel = item["snippet"]["channelTitle"].lower()
                country = item["snippet"].get("defaultAudioLanguage", "")

                lat, lon = CREATOR_LOCATIONS.get(
                    channel,
                    geocode_keyword(title)
                )

                sentiment = analyze(title)
                intensity = get_intensity(concurrent, max_velocity=500000)
                phase = get_phase(0)

                event = HeatEvent(
                    id=f"yt_{item['id']}",
                    type="youtube_live",
                    lat=lat,
                    lon=lon,
                    intensity=intensity,
                    sentiment=sentiment,
                    title=f"YouTube Live — {title[:80]}",
                    velocity=concurrent,
                    phase=phase
                )

                await redis_client.zadd(
                    "events",
                    {event.model_dump_json(): int(time.time())}
                )
                await redis_client.set(f"event:{event.id}", event.model_dump_json())
                print(f"[YouTube] Heat Event: {event.title}")

            await asyncio.sleep(30)

        except Exception as e:
            print(f"[YouTube Worker] Error: {e}")
            await asyncio.sleep(30)
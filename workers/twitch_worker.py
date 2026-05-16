import asyncio
import os
import time
import json
from dotenv import load_dotenv
from twitchAPI.twitch import Twitch
from core.models import HeatEvent
from core.geocoder import geocode_keyword
from core.sentiment import analyze
from core.threshold import is_heat_event, get_intensity, get_phase
from redis_client import redis_client

load_dotenv()

# Game studio locations for known games
GAME_LOCATIONS = {
    "fortnite": (35.6762, 139.6503),       # Epic (NC, USA)
    "valorant": (34.0522, -118.2437),       # Riot LA
    "league of legends": (34.0522, -118.2437),
    "minecraft": (59.3293, 18.0686),        # Mojang Stockholm
    "gta": (40.7128, -74.0060),             # Rockstar NYC
    "call of duty": (34.0522, -118.2437),
}

async def start():
    twitch = await Twitch(
        os.getenv("TWITCH_CLIENT_ID"),
        os.getenv("TWITCH_CLIENT_SECRET")
    )

    print("[Twitch Worker] Started")

    previous_viewers = {}

    while True:
        try:
            streams = []
            async for stream in twitch.get_streams(first=20):
                streams.append(stream)

            for stream in streams:
                game_name = stream.game_name.lower()
                viewer_count = stream.viewer_count
                prev = previous_viewers.get(game_name, 0)

                # detect sudden spike
                spike = viewer_count - prev
                previous_viewers[game_name] = viewer_count

                if not is_heat_event("twitch_viewers", viewer_count):
                    continue

                lat, lon = GAME_LOCATIONS.get(
                    game_name,
                    geocode_keyword(game_name)
                )

                sentiment = analyze(stream.title)
                phase = get_phase(0)  # fresh event
                intensity = get_intensity(viewer_count, max_velocity=200000)

                event = HeatEvent(
                    id=f"twitch_{stream.id}",
                    type="twitch_game",
                    lat=lat,
                    lon=lon,
                    intensity=intensity,
                    sentiment="hype",
                    title=f"Twitch — {stream.game_name} ({viewer_count:,} viewers)",
                    velocity=viewer_count,
                    phase=phase
                )

                await redis_client.zadd(
                    "events",
                    {event.model_dump_json(): int(time.time())}
                )
                await redis_client.set(f"event:{event.id}", event.model_dump_json())
                print(f"[Twitch] Heat Event: {event.title}")

            await asyncio.sleep(15)

        except Exception as e:
            print(f"[Twitch Worker] Error: {e}")
            await asyncio.sleep(20)
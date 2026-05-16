import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from api.websocket import websocket_endpoint, broadcast_loop
from redis_client import ping_redis

import workers.reddit_worker as reddit_worker
import workers.youtube_worker as youtube_worker
import workers.twitch_worker as twitch_worker
import workers.twitter_worker as twitter_worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # check Redis connection on startup
    try:
        await ping_redis()
        print("[Main] Redis connected OK")
    except Exception as e:
        print(f"[Main] Redis connection failed: {e}")

    # start all workers and the WS broadcast loop
    asyncio.create_task(reddit_worker.start())
    asyncio.create_task(youtube_worker.start())
    asyncio.create_task(twitch_worker.start())
    asyncio.create_task(twitter_worker.start())
    asyncio.create_task(broadcast_loop())

    print("[Main] All workers started")
    yield
    print("[Main] Shutting down")

app = FastAPI(title="NetPulse", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.add_api_websocket_route("/ws", websocket_endpoint)

@app.get("/")
async def root():
    return {"message": "NetPulse backend running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
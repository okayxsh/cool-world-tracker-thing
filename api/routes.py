from fastapi import APIRouter
from redis_client import redis_client

router = APIRouter(prefix="/api")

@router.get("/status")
async def status():
    return {"status": "ok", "bpm": 0}

@router.get("/history")
async def history(from_ts: int = 0, to_ts: int = 9999999999):
    events = await redis_client.zrangebyscore("events", from_ts, to_ts)
    return {"events": events}

@router.get("/events/{event_id}")
async def get_event(event_id: str):
    event = await redis_client.get(f"event:{event_id}")
    if not event:
        return {"error": "Event not found"}
    return {"event": event}
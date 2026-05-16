import asyncio
import json
import time
from fastapi import WebSocket, WebSocketDisconnect
from redis_client import redis_client
from core.models import Batch, HeatEvent

connected_clients: list[WebSocket] = []
batch_counter = 0

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print(f"[WS] Client connected. Total: {len(connected_clients)}")
    try:
        while True:
            await websocket.receive_text()  # keep connection alive
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(connected_clients)}")

async def broadcast_loop():
    """Runs every 500ms, batches new events and pushes to all clients."""
    global batch_counter

    while True:
        await asyncio.sleep(0.5)

        if not connected_clients:
            continue

        try:
            now = int(time.time())
            half_second_ago = now - 1  # grab last second of events

            raw_events = await redis_client.zrangebyscore(
                "events", half_second_ago, now
            )

            events = []
            for raw in raw_events:
                try:
                    events.append(HeatEvent.model_validate_json(raw))
                except Exception:
                    continue

            # calculate BPM (events per minute normalized to 0-200)
            bpm = min(len(events) * 60 * 2, 200)

            # global sentiment — most common sentiment in batch
            if events:
                sentiments = [e.sentiment for e in events]
                global_sentiment = max(set(sentiments), key=sentiments.count)
            else:
                global_sentiment = "neutral"

            batch_counter += 1
            batch = Batch(
                timestamp=now * 1000,
                batch_id=f"b_{batch_counter:04d}",
                events=events,
                global_sentiment=global_sentiment,
                bpm=bpm
            )

            message = batch.model_dump_json()

            # push to all connected clients
            disconnected = []
            for client in connected_clients:
                try:
                    await client.send_text(message)
                except Exception:
                    disconnected.append(client)

            for client in disconnected:
                connected_clients.remove(client)

        except Exception as e:
            print(f"[WS Batcher] Error: {e}")
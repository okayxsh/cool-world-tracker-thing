# 🌐 NetPulse — Real-Time Internet Activity Heatmap Globe

> A living, breathing 3D globe that visualizes the internet's chaos in real time — Reddit explosions, YouTube live spikes, Twitch meta shifts, and viral memes, all mapped to geography and pulsing with sentiment.

---

## Table of Contents

1. [Project Vision](#1-project-vision)
2. [The Core Visualization — The Globe](#2-the-core-visualization--the-globe)
3. [The "Chaos" Detection — Data Ingestion](#3-the-chaos-detection--data-ingestion)
4. [The Dashboard & HUD — User Interface](#4-the-dashboard--hud--user-interface)
5. [Technical "Magic" — Backend & Logic](#5-technical-magic--backend--logic)
6. [Social & Shareability](#6-social--shareability)
7. [Tech Stack](#7-tech-stack)
8. [Architecture Overview](#8-architecture-overview)
9. [Data Flow](#9-data-flow)
10. [API & Data Source Details](#10-api--data-source-details)
11. [Frontend Responsibilities](#11-frontend-responsibilities)
12. [Backend Responsibilities](#12-backend-responsibilities)
13. [Key Definitions & Glossary](#13-key-definitions--glossary)

---

## 1. Project Vision

NetPulse is a **real-time internet seismograph** — a 3D interactive globe that shows *where* the internet is going crazy, *why* it's going crazy, and *how intense* the chaos is. It ingests data from Reddit, YouTube, Twitch, and Twitter/X, geocodes it to real-world coordinates, and renders it as pulsing heat events on a WebGL globe.

The goal is to answer one question at a glance: **"What is the internet freaking out about right now, and where?"**

---

## 2. The Core Visualization — The Globe

### 2.1 Geospatial Mapping (Auto-Geocoding)

- Automatically geocodes **non-spatial data** to real-world coordinates.
- Examples of geocoding logic:
  - A spike in `r/london` → maps to London, UK (`51.5074, -0.1278`).
  - A trending hashtag `#Tokyo2026` → maps to Tokyo, Japan (`35.6762, 139.6503`).
  - A YouTube creator's known location (e.g., Kai Cenat in NYC) → maps to approximate coordinates.
- For data with **no geographic signal**, assign to a default "Global/Unknown" zone or infer from user demographics if available.

### 2.2 "Pulse" Decay System

This is the heartbeat of the visualization. Every event has a lifecycle:

| Phase | Visual | Description |
|---|---|---|
| **Ping** (0–30s) | Bright, small, high-frequency pulse | A new event just fired. Maximum intensity. |
| **Glow** (30s–5min) | Growing radius, slightly dimmer | The trend is still active but velocity is stabilizing. |
| **Cool** (5min–30min) | Large radius, very dim, slow pulse | The trend is losing steam. |
| **Ambient** (30min+) | Fades into background "night-lights" | The event is now part of the globe's baseline texture. |

- The **brightness** is tied to the event's **velocity** (rate of change), not its absolute size.
- The **radius** grows as the event ages.
- Events that **re-spike** (e.g., a second wave of comments) get re-promoted back to the "Ping" phase.

### 2.3 Atmospheric Sentiment (Globe Aura)

- The globe has an **outer atmospheric glow** — a translucent shell around the sphere.
- The aura color reflects the **global aggregate sentiment** across all active events:

| Sentiment | Aura Color | Example Triggers |
|---|---|---|
| Positive / Chill | Cyan / Light Blue | Wholesome memes, good news, celebrations |
| Neutral / Buzzing | White / Soft Yellow | General trending, mixed reactions |
| Controversial / Heated | Orange / Amber | Political debates, drama, heated discourse |
| Chaos / Anger | Deep Red / Crimson | Outrage events, cancellations, crises |
| Hype / Excitement | Electric Purple / Magenta | Game releases, trailer drops, live events |

- Sentiment is computed via **basic NLP** (keyword-based or lightweight model) on event headlines/titles.
- The aura transitions **smoothly** between colors (lerp over ~2 seconds).

### 2.4 Camera "Snap-to-Chaos"

- An **optional toggle** in the UI (default: OFF).
- When enabled, the globe **auto-rotates** to the latest "Explosion" event detected in real time.
- Smooth camera animation (ease-in-out) to the new coordinates.
- A small cooldown (e.g., 5 seconds) between snaps to prevent nausea-inducing rapid rotations.
- The user can always manually override by dragging the globe, which temporarily disables snap-to-chaos for ~10 seconds.

---

## 3. The "Chaos" Detection — Data Ingestion

### 3.1 Reddit "Explosion" Tracker

- **Monitors:** Specific subreddits — `r/all`, `r/gaming`, `r/news`, `r/worldnews`, `r/technology`, `r/movies`, and others (configurable).
- **Trigger Condition:** A post hits **1,000+ comments in under 5 minutes** → triggers a **"Heat Event."**
- **Metrics Tracked:**
  - Comment velocity (comments/minute).
  - Upvote velocity (upvotes/minute).
  - Award count acceleration.
- **Geocoding:** Derived from subreddit name, post title keywords, or flair (e.g., `r/london`, `[US]` flair).

### 3.2 YouTube Live Spike

- **Monitors:** YouTube's trending "Now Live" categories.
- **Trigger Condition:** A creator goes live and hits **100,000+ concurrent viewers** rapidly → triggers a **"Beacon Event."**
- **Visual:** A vertical **beacon/pillar** rising from the creator's approximate location on the globe.
- **Location:** Based on the creator's last known or approximate location (pre-mapped in a lookup table, or inferred from channel metadata).
- **Metrics Tracked:**
  - Concurrent viewer count.
  - Rate of viewer growth.
  - Chat message velocity.

### 3.3 Gaming "Meta" Shifts (Twitch)

- **Monitors:** Twitch category/game viewer counts.
- **Trigger Condition:** A game jumps from **0 → 50,000+ viewers** suddenly → flagged as a **"Gaming Trend."**
- **Examples:**
  - A surprise game announcement at a conference → instant spike.
  - A random indie game goes viral on Twitch.
- **Visual:** A distinct gaming-themed ping (e.g., controller icon or game-specific color).
- **Location:** Mapped to the game studio's HQ or the event's physical location (e.g., E3 → Los Angeles).

### 3.4 Breaking Meme Identifier (Twitter/X + Reddit NLP)

- **Source:** Trending Twitter/X topics and Reddit hot post titles.
- **Method:** Basic NLP — scans for **repeating keywords** across multiple posts/tweets within a short time window.
- **Clustering:** Groups related mentions into a single **"Meme Event"** (e.g., 500 tweets about "Silksong" in 10 minutes = 1 Meme Event, not 500 individual pings).
- **Examples:**
  - "GTA 6 Trailer" appearing across Reddit, Twitter, and YouTube simultaneously.
  - "Silksong release date" trending in multiple gaming communities.
- **Visual:** A pulsing cluster with the keyword displayed as a label on the globe.

---

## 4. The Dashboard & HUD — User Interface

### 4.1 Real-Time Ticker (Bottom Bar)

- A **horizontal scrolling ticker** at the bottom of the screen.
- Shows a **"Firehose"** of raw events as they come in.
- Format: `[HH:MM:SS] EVENT_TYPE: source - detail`
- Examples:
  ```
  [22:41:04] SPIKE: r/worldnews — +4,200 upvotes/min
  [22:41:06] LIVE:  YouTube — KaiCenat hit 250k viewers
  [22:41:09] MEME:  Twitter/X — "GTA 6" trending in 14 countries
  [22:41:12] GAME:  Twitch — "Balatro 2" jumped 0 → 85k viewers
  ```
- Color-coded by event type.
- Clicking a ticker item should **snap the globe** to that event's location and open the drill-down card.

### 4.2 "Internet Pulse" Metric (BPM — Bits Per Minute)

- A single, prominent **"heart rate" number** displayed in the HUD.
- Measures the **overall speed of data flowing** through the backend.
- Calculated as: total events ingested per minute, normalized to a 0–200 BPM scale.
- Visual: An **animated heart/pulse line** (like an ECG) that beats faster when the internet is chaotic.
- Baseline: ~60 BPM during quiet hours, spikes to 180+ during major events.

### 4.3 Trend Drill-Down (Glassmorphism Side Card)

- Triggered by **clicking a heat-spot** on the globe.
- Opens a **slide-in side panel** with a glassmorphism aesthetic (frosted glass, blurred background, subtle border glow).
- Contents:

| Section | Description |
|---|---|
| **Event Title** | The trend name or keyword (e.g., "GTA 6 Trailer Drop") |
| **Top 3 Links** | Direct links to the most relevant Reddit posts / tweets / streams |
| **Sentiment Breakdown** | A mini bar chart — % Happy, % Angry, % Neutral, % Hype |
| **Origin Point** | Where the trend was **first detected** (source + timestamp) |
| **Velocity Graph** | A small sparkline showing event velocity over the last 30 min |
| **Related Events** | Other active events that share keywords |

---

## 5. Technical "Magic" — Backend & Logic

### 5.1 The WebSocket Batcher

- The backend does **NOT** push every single event individually to the frontend.
- Instead, it **batches** all events that occurred in the last **500ms** into a **single JSON packet**.
- This keeps the React frontend rendering at a **smooth 60fps** without being overwhelmed by event storms.
- Batch format:
  ```json
  {
    "timestamp": 1718486464000,
    "batch_id": "b_0042",
    "events": [
      {
        "id": "evt_001",
        "type": "reddit_spike",
        "lat": 51.5074,
        "lon": -0.1278,
        "intensity": 0.92,
        "sentiment": "controversial",
        "title": "r/worldnews — Breaking: ...",
        "velocity": 4200,
        "phase": "ping"
      }
    ],
    "global_sentiment": "heated",
    "bpm": 142
  }
  ```

### 5.2 Rate-Limit Management (Worker Layer)

- A dedicated **"Worker" layer** sits between the backend and external APIs.
- Responsibilities:
  - **API key rotation:** Cycles through multiple API keys to stay within rate limits.
  - **Scraper fallback:** If API limits are exhausted, falls back to lightweight scrapers (with respectful delays).
  - **Request queuing:** Prioritizes high-velocity events over routine polling.
  - **Backoff logic:** Exponential backoff on 429 (Too Many Requests) responses.
- Platforms and their rate-limit considerations:
  - **Reddit API:** 60 requests/min per OAuth token. Rotate multiple tokens.
  - **YouTube Data API:** 10,000 units/day quota. Use sparingly; supplement with scraping.
  - **Twitch API (Helix):** 800 requests/min. Relatively generous.
  - **Twitter/X API:** Heavily restricted on free tier. May need to rely on scraping or third-party aggregators.

### 5.3 Historical Scrubbing (Redis Rewind Buffer)

- A **circular buffer** stored in **Redis** that retains the last **1 hour** of event data.
- Enables the user to **"rewind" the globe** via a timeline slider in the UI.
- Use case: See how a trend **traveled across the world** over time (e.g., a meme starting in Japan, spreading to Europe, then hitting the US).
- Data structure: Redis Sorted Set keyed by timestamp.
- Oldest entries are **automatically evicted** after 1 hour (TTL-based or manual trimming).
- On rewind, the frontend replays batches from the buffer at adjustable speed (1x, 2x, 5x, 10x).

---

## 6. Social & Shareability

### 6.1 "Live POV" Sharing

- A **share button** in the UI generates a URL encoding the current globe view.
- URL format: `netpulse.com/view?lat=35.6&lon=139.7&zoom=4&event=evt_001`
- Parameters:
  - `lat` / `lon` — Camera coordinates.
  - `zoom` — Zoom level.
  - `event` (optional) — Focused event ID (auto-opens the drill-down card).
- When someone opens the link, the globe animates to that exact view.

### 6.2 Chaos Alert System

- Users can configure **keyword-based alerts** (e.g., "AI," "Crypto," "Nvidia," "Silksong").
- When a keyword's associated events cross a configurable **heat threshold**, the alert fires.
- Alert behavior:
  - The **sidebar flashes red** with a notification badge.
  - Optional: Browser push notification.
  - Optional: Sound effect (a subtle "ping" or alarm).
- Alert configuration stored in **localStorage** (no auth needed for MVP) or user accounts later.

---

## 7. Tech Stack

### Frontend

| Technology | Purpose |
|---|---|
| **React** | UI framework, component architecture |
| **Vite** | Build tool, dev server, HMR |
| **TypeScript (TSX)** | Type safety, better DX |
| **Three.js / React Three Fiber** | 3D globe rendering (WebGL) |
| **WebSocket (client)** | Real-time data stream from backend |
| **CSS (Vanilla)** | Styling — glassmorphism, animations, HUD |

### Backend

| Technology | Purpose |
|---|---|
| **Python** | Primary backend language |
| **FastAPI** | HTTP API + WebSocket server |
| **WebSockets** | Real-time push to frontend |
| **Redis** | Event buffer (1-hour rewind), caching |
| **PRAW / asyncpraw** | Reddit API client |
| **Tweepy / snscrape** | Twitter/X data |
| **google-api-python-client** | YouTube Data API |
| **twitchAPI** | Twitch Helix API |
| **spaCy / TextBlob / VADER** | Lightweight NLP for sentiment + keyword extraction |

### Infrastructure (Future / Production)

| Technology | Purpose |
|---|---|
| **Docker** | Containerization |
| **Nginx** | Reverse proxy, static file serving |
| **PostgreSQL** | Persistent storage (if needed beyond Redis) |
| **Celery / asyncio tasks** | Background workers for scraping |

---

## 8. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                  │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐   │
│  │ 3D Globe │  │ Ticker   │  │ HUD/BPM  │  │ Drill-Down    │   │
│  │ (Three.js)│  │ (Bottom) │  │ (Overlay)│  │ (Side Panel)  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───────┬───────┘   │
│       │              │             │                │           │
│       └──────────────┴─────────────┴────────────────┘           │
│                          │                                      │
│                    WebSocket Client                             │
└────────────────────────┬────────────────────────────────────────┘
                         │ ws://
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI + Python)                  │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────────┐     │
│  │ WebSocket    │   │ Event        │   │ Sentiment       │     │
│  │ Batcher      │◄──│ Aggregator   │◄──│ Analyzer (NLP)  │     │
│  │ (500ms)      │   │              │   │                 │     │
│  └──────────────┘   └──────┬───────┘   └────────┬────────┘     │
│                            │                    │              │
│                     ┌──────┴────────────────────┘              │
│                     ▼                                          │
│          ┌─────────────────┐                                   │
│          │  Redis Buffer   │                                   │
│          │  (1-hour ring)  │                                   │
│          └─────────────────┘                                   │
│                     ▲                                          │
│                     │                                          │
│  ┌──────────────────┴──────────────────────────────────────┐   │
│  │              WORKER LAYER (Scrapers / API Clients)      │   │
│  │                                                         │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────┐  │   │
│  │  │ Reddit  │ │ YouTube │ │ Twitch  │ │ Twitter/X    │  │   │
│  │  │ Worker  │ │ Worker  │ │ Worker  │ │ Worker       │  │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Data Flow

```
1. Workers poll external APIs (Reddit, YouTube, Twitch, Twitter/X)
           │
           ▼
2. Raw data is processed:
   - Geocoded (subreddit name → lat/lon, creator → location)
   - Sentiment analyzed (headline → positive/negative/neutral)
   - Velocity calculated (comments/min, viewers/min)
           │
           ▼
3. Events that meet threshold conditions become "Heat Events"
           │
           ▼
4. Heat Events are stored in Redis (sorted set, keyed by timestamp)
           │
           ▼
5. Event Aggregator collects all new events
           │
           ▼
6. WebSocket Batcher bundles events every 500ms into a JSON packet
           │
           ▼
7. Packet is pushed to all connected frontend clients via WebSocket
           │
           ▼
8. Frontend renders events on the 3D globe with appropriate visuals
   - Ping / Glow / Cool / Ambient phase
   - Updates aura color
   - Updates ticker, BPM, etc.
```

---

## 10. API & Data Source Details

### Reddit (via PRAW / asyncpraw)

- **Endpoint:** Reddit OAuth2 API
- **Polling interval:** Every ~10 seconds on monitored subreddits
- **Data extracted:** Post title, comment count, upvote count, subreddit, flair, timestamp
- **Rate limit:** 60 requests/min per token
- **Geocoding strategy:** Subreddit name matching, title keyword extraction, flair tags

### YouTube (via YouTube Data API v3)

- **Endpoint:** `search.list` (type=video, eventType=live), `videos.list` (for stats)
- **Polling interval:** Every ~30 seconds
- **Data extracted:** Channel name, concurrent viewers, category, channel country
- **Rate limit:** 10,000 quota units/day (search = 100 units each — be careful)
- **Geocoding strategy:** Channel country metadata, pre-mapped creator lookup table

### Twitch (via Twitch Helix API)

- **Endpoint:** `streams`, `games/top`
- **Polling interval:** Every ~15 seconds
- **Data extracted:** Game name, viewer count, streamer name, language
- **Rate limit:** 800 requests/min
- **Geocoding strategy:** Game studio HQ lookup, event location mapping

### Twitter/X

- **Endpoint:** Trending topics API (if accessible), or scraping fallback
- **Polling interval:** Every ~20 seconds
- **Data extracted:** Trending hashtags, tweet text samples, tweet volume
- **Rate limit:** Heavily restricted on free tier — may rely on scraping
- **Geocoding strategy:** Hashtag keyword extraction, trending location metadata

---

## 11. Frontend Responsibilities

| Responsibility | Details |
|---|---|
| **Globe Rendering** | Three.js / React Three Fiber — textured Earth sphere, custom shaders for heat spots |
| **Event Visualization** | Render pings with decay lifecycle (brightness, radius, color) |
| **Aura Rendering** | Translucent outer shell with color lerping based on global sentiment |
| **WebSocket Connection** | Connect to backend, parse batched JSON, update state |
| **Ticker Bar** | Scrolling event feed, color-coded, clickable |
| **BPM Display** | Animated ECG line + numeric display |
| **Drill-Down Panel** | Glassmorphism side card with event details |
| **Timeline Slider** | Rewind control (fetches historical batches from backend) |
| **Snap-to-Chaos Toggle** | Camera auto-rotation to latest explosion |
| **Share Button** | Generate POV URL with current camera state |
| **Alert Config UI** | Keyword input + threshold slider, stored in localStorage |
| **Responsive Design** | Works on desktop (primary) and tablet |

---

## 12. Backend Responsibilities

| Responsibility | Details |
|---|---|
| **API Server** | FastAPI — serves REST endpoints + WebSocket |
| **WebSocket Manager** | Manages connected clients, pushes batched events every 500ms |
| **Worker Orchestration** | Spawns and manages async workers for each data source |
| **Geocoding Service** | Lookup tables + keyword matching to map events → coordinates |
| **Sentiment Analysis** | Lightweight NLP pipeline (VADER / TextBlob) on event titles |
| **Threshold Engine** | Evaluates if raw data meets "Heat Event" criteria |
| **Redis Management** | Writes events to sorted set, handles TTL, serves rewind queries |
| **Rate-Limit Handler** | API key rotation, backoff, scraper fallback |
| **REST Endpoints** | `GET /api/history?from=&to=` — rewind data |
| | `GET /api/events/:id` — single event detail |
| | `GET /api/status` — backend health + BPM |
| | `GET /api/alerts/check?keyword=` — alert threshold check |

---

## 13. Key Definitions & Glossary

| Term | Definition |
|---|---|
| **Heat Event** | Any data point that crosses the threshold to be rendered on the globe |
| **Ping** | The initial, brightest phase of a Heat Event (0–30s) |
| **Explosion** | A Heat Event with extreme velocity — triggers snap-to-chaos |
| **Beacon** | A vertical pillar visual used for YouTube Live events |
| **BPM (Bits Per Minute)** | Normalized metric representing overall internet activity speed |
| **Aura** | The globe's atmospheric glow reflecting aggregate sentiment |
| **Meme Event** | A cluster of related mentions grouped into a single entity via NLP |
| **Velocity** | The rate of change of a metric (comments/min, viewers/min, etc.) |
| **Decay** | The process of a Heat Event transitioning from Ping → Glow → Cool → Ambient |
| **Batch** | A 500ms bundle of events sent over WebSocket as a single JSON packet |
| **Rewind** | Replaying historical event data from the Redis buffer (up to 1 hour) |
| **Snap-to-Chaos** | Auto-camera rotation to the location of the latest Explosion |
| **Chaos Alert** | User-defined keyword watch that fires when a threshold is crossed |
| **POV URL** | A shareable link encoding the globe's camera position and focused event |
| **Worker** | A background async task that polls a specific data source |
| **Glassmorphism** | A UI design style featuring frosted-glass panels with blur + transparency |

---

> **Status:** 📋 Specification Complete — Awaiting build phase.

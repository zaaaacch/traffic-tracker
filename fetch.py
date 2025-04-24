#!/usr/bin/env python3
import os, requests, psycopg, datetime
GOOGLE_KEY  = os.environ["GOOGLE_KEY"]
NEON_CONN   = os.environ["NEON_CONN"]

# 1. call Google Directions
payload = {
    "origin":      {"address": "1886 Amelia Oaks Dr, Fernandina Beach, FL"},
    "destination": {"address": "96178 Sea Winds Dr, Fernandina Beach, FL"},
    "routingPreference": "TRAFFIC_AWARE"
}
r = requests.post(
    "https://routes.googleapis.com/directions/v2:computeRoutes?fields=routes.legs.duration",
    headers={
        "Content-Type": "application/json",
        "X-Goog-FieldMask": "*",
        "X-Goog-Api-Key": GOOGLE_KEY
    },
    json=payload,
    timeout=20,
)
r.raise_for_status()
seconds = int(r.json()["routes"][0]["legs"][0]["duration"][:-1])  # "347s" -> 347

# 2. save to Neon
with psycopg.connect(NEON_CONN, autocommit=True) as conn:
    with conn.cursor() as cur:
        cur.execute("""
          create table if not exists durations(
            id bigserial primary key,
            fetched_at timestamptz default now(),
            seconds int not null
          );
        """)
        cur.execute("insert into durations(seconds) values (%s)", (seconds,))
print(f"saved {seconds}s at {datetime.datetime.utcnow().isoformat()}Z")

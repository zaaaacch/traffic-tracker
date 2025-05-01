#!/usr/bin/env python3
import os, requests, datetime
import sqlite3
import psycopg
from dotenv import load_dotenv
import schedule
import time
load_dotenv()

GOOGLE_KEY  = os.environ.get("GOOGLE_KEY")
DB_PATH     = os.environ.get("DB_PATH", "durations.db")

def fetch_and_save():
    # 1. call Google Directions
    payload = {
      "origin": {
        "location": {
          "latLng": {
            "latitude":  30.631357799405247,
            "longitude": -81.4705143820595
          }
        }
      },
      "destination": {
        "location": {
          "latLng": {
            "latitude":  30.6706931032008,
            "longitude": -81.45884030610989
          }
        }
      },

      "travelMode":        "DRIVE",
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

    # 2. save to SQLite
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
      create table if not exists durations(
        id integer primary key autoincrement,
        fetched_at text default (datetime('now')),
        seconds integer not null
      );
    """)
    cur.execute("insert into durations(seconds) values (?)", (seconds,))
    conn.commit()
    conn.close()
    print(f"saved {seconds}s at {datetime.datetime.utcnow().isoformat()}Z")

if __name__ == "__main__":
    schedule.every(5).minutes.do(fetch_and_save)
    print("Scheduler started, fetching every 5 minutes...")
    fetch_and_save()
    while True:
        schedule.run_pending()
        time.sleep(1)

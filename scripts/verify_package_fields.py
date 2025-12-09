import asyncio
import httpx
import os
from api import config

async def check_live_package(event_id: str):
    """Fetch package for a real event ID to verify new fields."""
    url = f"http://localhost:8000/api/events/{event_id}/package"
    async with httpx.AsyncClient() as client:
        try:
            print(f"Fetching package for {event_id}...")
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                event = data.get("event", {})
                print("\n[SUCCESS] Package fetched!")
                print(f"Event: {event.get('text')}")
                print(f"Price: {event.get('min_price')} - {event.get('max_price')} {event.get('currency')}")
                print(f"Location: {event.get('venue_lat')}, {event.get('venue_lng')}")
            else:
                print(f"[ERROR] Failed to fetch package: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    # Use a likely real ID or just test against local if passing known ID
    # For now, we'll try to fetch events first to get a valid ID
    async def run():
        # First fetch an event list to get a real ID to test package
        list_url = "http://localhost:8000/api/events?date=2025-12-15&country_code=US"
        async with httpx.AsyncClient() as client:
            print("Fetching events list to find a target ID...")
            resp = await client.get(list_url)
            if resp.status_code == 200:
                events = resp.json()
                if events:
                    target_id = events[0]["id"]
                    print(f"Found event ID: {target_id}")
                    await check_live_package(target_id)
                else:
                    print("No events found to test package against.")
            else:
                print("Failed to list events.")

    asyncio.run(run())

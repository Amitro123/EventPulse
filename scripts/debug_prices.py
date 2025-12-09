import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Search for events by Artist
        resp = await client.get("http://localhost:8000/api/events/by-artist?artist=Coldplay&country_code=US&limit=5")
        if resp.status_code != 200:
            print(f"Error: {resp.status_code}")
            return
            
        events = resp.json()
        print(f"Found {len(events)} events")
        for e in events:
            print(f"\nID: {e.get('id')}")
            print(f"Name: {e.get('text')}")
            print(f"Min Price: {e.get('min_price')} ({type(e.get('min_price'))})")
            print(f"Max Price: {e.get('max_price')}")
            print(f"Currency: {e.get('currency')}")
            print(f"Old Price Range String: {e.get('price_range')}")

if __name__ == "__main__":
    asyncio.run(main())

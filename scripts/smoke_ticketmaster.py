import argparse
import asyncio
import os
import sys
from datetime import datetime

# Allow importing from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.collectors.ticketmaster import collect_events
from api import config

async def main():
    parser = argparse.ArgumentParser(description="Smoke test Ticketmaster integration (Live Mode)")
    parser.add_argument("--date", type=str, default=datetime.now().strftime("%Y-%m-%d"), help="Date (YYYY-MM-DD)")
    parser.add_argument("--country", type=str, default="US", help="Country code (default: US)")
    parser.add_argument("--city", type=str, default=None, help="City name")
    
    args = parser.parse_args()
    
    print(f"--- Ticketmaster Live Smoke Test ---")
    print(f"Date: {args.date}")
    print(f"Country: {args.country}")
    if args.city:
        print(f"City: {args.city}")
    print(f"API Key Present: {bool(config.TICKETMASTER_API_KEY and not config.TICKETMASTER_API_KEY.startswith('your_'))}")
    print("-" * 30)
    
    try:
        events = await collect_events(
            date=args.date,
            country_code=args.country,
            city=args.city,
            limit=5
        )
        
        print(f"\nFound {len(events)} events:")
        for i, e in enumerate(events[:5]):
            print(f" {i+1}. [{e.timestamp}] {e.text} @ {e.venue_name} ({e.city})")
            print(f"    URL: {e.url}")
            if e.price_range:
                print(f"    Price: {e.price_range}")
        
        if not events:
            print("No events found (this might be valid if no events match)")
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

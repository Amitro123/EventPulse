"""Ticketmaster API collector for event discovery."""
import httpx
from typing import List, Optional
from api.models.event import EventMention
from api import config
from api.collectors.base import EventCollector, EventSearchQuery, ArtistSearchQuery


class TicketmasterCollector(EventCollector):
    """Collector for Ticketmaster Discovery API."""

    def __init__(self):
        self.base_url = f"{config.TICKETMASTER_BASE_URL}/events.json"

    async def search(self, query: EventSearchQuery) -> List[EventMention]:
        """Collect events from Ticketmaster Discovery API."""
        # Check if API key is missing or is a placeholder value
        api_key = config.TICKETMASTER_API_KEY
        is_placeholder = not api_key or api_key.startswith("your_") or api_key == "test"
        
        if is_placeholder:
            print("[INFO] Mock Mode: No valid Ticketmaster API key configured")
            return self._get_mock_events(query.date, query.city, query.category)
        
        params = {
            "apikey": config.TICKETMASTER_API_KEY,
            "countryCode": query.country_code,
            "localStartDateTime": f"{query.date}T00:00:00,{query.date}T23:59:59",
            "size": query.limit,
            "sort": "date,asc",
            "page": query.page
        }
        
        if query.city:
            params["city"] = query.city
        if query.category:
            params["classificationName"] = query.category
        
        return await self._fetch_events(params, query.date, query.city, query.category)

    async def search_by_artist(self, query: ArtistSearchQuery) -> List[EventMention]:
        """Search events by artist name using Ticketmaster Discovery API."""
        # Check if API key is missing or is a placeholder value
        api_key = config.TICKETMASTER_API_KEY
        is_placeholder = not api_key or api_key.startswith("your_") or api_key == "test"
        
        if is_placeholder:
            print("[INFO] No valid Ticketmaster API key configured, using mock artist data")
            return self._get_mock_artist_events(query.artist, query.date_from)
        
        params = {
            "apikey": config.TICKETMASTER_API_KEY,
            "keyword": query.artist,
            "countryCode": query.country_code,
            "size": query.limit,
            "sort": "date,asc",
            "page": query.page
        }
        
        # Add optional date range filters
        if query.date_from and query.date_to:
            params["localStartDateTime"] = f"{query.date_from}T00:00:00,{query.date_to}T23:59:59"
        elif query.date_from:
            params["localStartDateTime"] = f"{query.date_from}T00:00:00,*"
        elif query.date_to:
            params["localStartDateTime"] = f"*,{query.date_to}T23:59:59"
            
        return await self._fetch_events(params, query.date_from or "")

    async def _fetch_events(self, params: dict, default_date: str, city_filter: str = None, category_filter: str = None) -> List[EventMention]:
        """Internal method to execute the HTTP request and parse results."""
        events: List[EventMention] = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                print(f"[INFO] Fetching events from Ticketmaster...")
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if "_embedded" not in data or "events" not in data["_embedded"]:
                    return events
                
                for e in data["_embedded"]["events"]:
                    # Refactored Extraction Logic
                    venue_name = "TBA"
                    event_city = city_filter or "Unknown"
                    if "_embedded" in e and "venues" in e["_embedded"] and e["_embedded"]["venues"]:
                        venue = e["_embedded"]["venues"][0]
                        venue_name = venue.get("name", "TBA")
                        if "city" in venue:
                            event_city = venue["city"].get("name", event_city)
                    
                    price_range, min_price, max_price, currency = self._extract_price_info(e)
                    venue_lat, venue_lng = self._extract_location(e)
                    
                    # Extract image
                    image_url = None
                    if "images" in e and e["images"]:
                        images = sorted(e["images"], key=lambda x: x.get("width", 0), reverse=True)
                        image_url = images[0].get("url")

                    # Extract category
                    category = category_filter or "music"
                    if "classifications" in e and e["classifications"]:
                         category = e["classifications"][0].get("segment", {}).get("name", "music").lower()

                    events.append(EventMention(
                        id=e["id"],
                        text=e.get("name", "Unknown Event"),
                        url=e.get("url", ""),
                        timestamp=e.get("dates", {}).get("start", {}).get("localDate", default_date),
                        venue_name=venue_name,
                        city=event_city,
                        category=category,
                        image_url=image_url,
                        price_range=price_range,
                        min_price=min_price,
                        max_price=max_price,
                        currency=currency,
                        venue_lat=venue_lat,
                        venue_lng=venue_lng,
                        scores={"popularity": e.get("score", 0)},
                        raw_data=e,
                        provider="ticketmaster"
                    ))
            except Exception as e:
                print(f"[ERROR] Ticketmaster API error: {e}")
        
        return events

    def _extract_price_info(self, e: dict):
        price_range = None
        min_price = None
        max_price = None
        currency = None
        if "priceRanges" in e and e["priceRanges"]:
            pr = e["priceRanges"][0]
            min_price = pr.get("min")
            max_price = pr.get("max")
            currency = pr.get("currency")
            if min_price is not None and max_price is not None:
                price_range = f"${min_price:.0f} - ${max_price:.0f}"
        return price_range, min_price, max_price, currency

    def _extract_location(self, e: dict):
        venue_lat = None
        venue_lng = None
        if "_embedded" in e and "venues" in e["_embedded"] and e["_embedded"]["venues"]:
                v_obj = e["_embedded"]["venues"][0]
                if "location" in v_obj:
                    venue_lat = float(v_obj["location"].get("latitude", 0)) or None
                    venue_lng = float(v_obj["location"].get("longitude", 0)) or None
        return venue_lat, venue_lng

    def _get_mock_events(self, date: str, city: Optional[str] = None, category: Optional[str] = None) -> List[EventMention]:
        """Return mock events."""
        default_city = city or "Tel Aviv"
        default_category = category or "music"
        return [
            EventMention(
                id="mock-1",
                text="Coldplay - Music of the Spheres World Tour",
                url="https://www.ticketmaster.com/coldplay-tickets/artist/806431",
                timestamp=date,
                venue_name="Bloomfield Stadium",
                city=default_city,
                category=default_category,
                image_url="https://via.placeholder.com/300x200?text=Coldplay",
                price_range="$150 - $450",
                min_price=150.0, max_price=450.0, currency="USD",
                scores={"popularity": 0.95},
                provider="ticketmaster"
            ),
             EventMention(
                id="mock-2",
                text="Ed Sheeran - Mathematics Tour",
                url="https://www.ticketmaster.com/ed-sheeran-tickets/artist/1616239",
                timestamp=date,
                venue_name="Yarkon Park",
                city=default_city,
                category=default_category,
                image_url="https://via.placeholder.com/300x200?text=Ed+Sheeran",
                price_range="$120 - $380",
                min_price=120.0, max_price=380.0, currency="USD",
                scores={"popularity": 0.92},
                provider="ticketmaster"
            ),
        ]

    def _get_mock_artist_events(self, artist: str, date_from: Optional[str] = None) -> List[EventMention]:
        """Return mock artist events."""
        base_date = date_from or "2025-06-15"
        return [
            EventMention(
                id="artist-mock-1",
                text=f"{artist} - Live in Concert",
                url=f"https://www.ticketmaster.com/search?q={artist.replace(' ', '+')}",
                timestamp=base_date,
                venue_name="Madison Square Garden",
                city="New York",
                category="music",
                image_url=f"https://via.placeholder.com/300x200?text={artist.replace(' ', '+')}",
                price_range="$75 - $350",
                min_price=75.0, max_price=350.0, currency="USD",
                scores={"popularity": 0.90},
                provider="ticketmaster"
            )
        ]

# Helper functions for backward compatibility (during refactor)
_collector = TicketmasterCollector()

async def collect_events(date: str, city: Optional[str] = None, category: Optional[str] = None, limit: int = 20, country_code: str = "IL", page: int = 0) -> List[EventMention]:
    query = EventSearchQuery(date, city, category, limit, country_code, page)
    return await _collector.search(query)

async def search_by_artist(artist: str, date_from: Optional[str] = None, date_to: Optional[str] = None, country_code: str = "US", limit: int = 20, page: int = 0) -> List[EventMention]:
    query = ArtistSearchQuery(artist, date_from, date_to, country_code, limit, page)
    return await _collector.search_by_artist(query)

def _get_mock_events(date: str, city: Optional[str] = None, category: Optional[str] = None) -> List[EventMention]:
    return _collector._get_mock_events(date, city, category)



"""Ticketmaster API collector for event discovery."""
import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from api.models.event import EventMention
from api import config
from api.collectors.base import EventCollector, EventSearchQuery, ArtistSearchQuery

logger = logging.getLogger(__name__)


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
            logger.info("Mock Mode: No valid Ticketmaster API key configured")
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
        
        # Call real API - return results or empty list, never mock data
        events, _ = await self._fetch_events(params, query.date, query.city, query.category)
        return events

    async def search_by_artist(self, query: ArtistSearchQuery) -> Tuple[List[EventMention], int]:
        """Search events by artist name using Ticketmaster Discovery API."""
        # Check if API key is missing or is a placeholder value
        api_key = config.TICKETMASTER_API_KEY
        is_placeholder = not api_key or api_key.startswith("your_") or api_key == "test"
        
        if is_placeholder:
            logger.info("No valid Ticketmaster API key configured, using mock artist data")
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
            
        # Call real API - return results or empty list, never mock data
        return await self._fetch_events(params, query.date_from or "")

    async def resolve_event(self, name: str, city: str, date: str) -> Optional[EventMention]:
        """
        Try to find a specific Ticketmaster event by name, city, and exact date.
        Used to resolve Ticketmaster links for events discovered via other providers.
        """
        api_key = config.TICKETMASTER_API_KEY
        is_placeholder = not api_key or api_key.startswith("your_") or api_key == "test"
        
        if is_placeholder:
            # In mock mode, check if name matches our mock Coldplay event
            if "Coldplay" in name and "Tel Aviv" in city:
                mock_events = self._get_mock_events(date, city)
                return mock_events[0] if mock_events else None
            return None

        params = {
            "apikey": config.TICKETMASTER_API_KEY,
            "keyword": name,
            "city": city,
            "localStartDateTime": f"{date}T00:00:00,{date}T23:59:59",
            "size": 1
        }
        
        results, _ = await self._fetch_events(params, date, city)
        return results[0] if results else None

    async def _fetch_events(self, params: dict, default_date: str, city_filter: str = None, category_filter: str = None) -> Tuple[List[EventMention], int]:
        """Internal method to execute the HTTP request and parse results."""
        events: List[EventMention] = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                logger.info("Fetching events from Ticketmaster...")
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if "_embedded" not in data or "events" not in data["_embedded"]:
                    return events, 0
                
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

                    # Fix: Ensure URL is present for Ticketmaster events
                    event_url = e.get("url", "")
                    if not event_url and "id" in e:
                         # Fallback to constructing URL from ID
                         event_url = f"https://www.ticketmaster.com/event/{e['id']}"

                    # Determine if it has tickets (not cancelled)
                    has_tickets = e.get("dates", {}).get("status", {}).get("code") != "cancelled"

                    events.append(EventMention(
                        id=e["id"],
                        text=e.get("name", "Unknown Event"),
                        url=event_url,
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
                        provider="ticketmaster",
                        ticket_provider="ticketmaster",
                        has_tickets=has_tickets
                    ))
            except httpx.HTTPError as e:
                logger.error(f"HTTP error fetching events from Ticketmaster: {e}", exc_info=True)
            except Exception as e:
                logger.exception(f"Unexpected error fetching events from Ticketmaster: {e}")
        
        # Extract total count from pagination metadata
        total_elements = 0
        try:
            if "page" in data and "totalElements" in data["page"]:
                total_elements = data["page"]["totalElements"]
        except (KeyError, TypeError, UnboundLocalError):
             pass

        return events, total_elements

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
                provider="ticketmaster",
                ticket_provider="ticketmaster",
                has_tickets=True
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
                provider="ticketmaster",
                ticket_provider="ticketmaster",
                has_tickets=True
            ),
        ]

    def _get_mock_artist_events(self, artist: str, date_from: Optional[str] = None) -> Tuple[List[EventMention], int]:
        """Return multiple mock artist events for a more realistic testing experience."""
        base_date = date_from or "2025-06-15"
        base_dt = datetime.strptime(base_date, "%Y-%m-%d")
        
        # Realistic tour names for the mock results
        tour_names = [
            "LOOP Tour",
            "Live in Concert",
            "Mathematics Tour",
            "World Tour",
            "Summer Festival Appearance"
        ]
        
        # Realistic venues for the mock results
        venues = [
            ("Madison Square Garden", "New York"),
            ("O2 Arena", "London"),
            ("Stade de France", "Paris"),
            ("Wembley Stadium", "London"),
            ("Red Rocks Amphitheatre", "Morrison")
        ]
        
        mock_events = []
        for i in range(25):
            tour_name = tour_names[i % len(tour_names)]
            venue_name, city = venues[i % len(venues)]
            # Space out the dates slightly for the mock results
            event_date = (base_dt + timedelta(days=i*14)).strftime("%Y-%m-%d")
            
            mock_events.append(EventMention(
                id=f"artist-mock-{i+1}",
                text=f"{artist} - {tour_name}",
                url=f"https://www.ticketmaster.com/search?q={artist.replace(' ', '+')}",
                timestamp=event_date,
                venue_name=venue_name,
                city=city,
                category="music",
                image_url=f"https://via.placeholder.com/300x200?text={artist.replace(' ', '+')}+{i+1}",
                price_range=f"${75 + i*10} - ${350 + i*50}",
                min_price=float(75 + i*10), 
                max_price=float(350 + i*50), 
                currency="USD",
                scores={"popularity": 0.90 - i*0.02},
                provider="ticketmaster",
                ticket_provider="ticketmaster",
                has_tickets=True
            ))
            
        return mock_events, len(mock_events)

# The legacy standalone helper functions (collect_events, search_by_artist, _get_mock_events)



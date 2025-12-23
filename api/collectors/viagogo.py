"""Viagogo collector for event discovery.

This collector searches for events using Viagogo as a data source.
Currently uses mock data - swap the mock methods for real API calls
when Viagogo API becomes available.
"""
import httpx
from typing import List, Optional
from api.models.event import EventMention
from api import config
from api.collectors.base import EventCollector, EventSearchQuery, ArtistSearchQuery


class ViagogoCollector(EventCollector):
    """
    Collector for Viagogo event discovery.
    
    Currently operates in mock mode (USE_VIAGOGO_MOCK=true).
    To integrate a real API in the future:
    1. Set USE_VIAGOGO_MOCK=false
    2. Implement _fetch_events_from_api() method
    3. Map Viagogo API response to EventMention model
    """

    def __init__(self):
        self.base_url = config.VIAGOGO_BASE_URL
        self.affiliate_id = config.VIAGOGO_AFFILIATE_ID
        self.use_mock = config.USE_VIAGOGO_MOCK

    async def search(self, query: EventSearchQuery) -> List[EventMention]:
        """Search events by date/location using Viagogo."""
        if self.use_mock:
            return self._get_mock_events(query.date, query.city, query.category)
        
        # TODO: Implement real Viagogo API call when available
        # return await self._fetch_events_from_api(query)
        return []

    async def search_by_artist(self, query: ArtistSearchQuery) -> List[EventMention]:
        """Search events by artist using Viagogo."""
        if self.use_mock:
            return self._get_mock_artist_events(query.artist, query.date_from)
        
        # TODO: Implement real Viagogo API call when available
        # return await self._fetch_artist_events_from_api(query)
        return []

    def _build_viagogo_url(self, event_slug: str) -> str:
        """Build a Viagogo event URL with affiliate parameter."""
        return f"{self.base_url}/event/{event_slug}?affiliateId={self.affiliate_id}"

    def _get_mock_events(
        self,
        date: str,
        city: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[EventMention]:
        """Return mock Viagogo events for testing."""
        default_city = city or "New York"
        default_category = category or "music"
        
        # Generate viagogo URLs for fallback ticket source
        events = [
            EventMention(
                id="viagogo-1",
                text="Bruno Mars - 24K Magic World Tour",
                url=self._build_viagogo_url("bruno-mars-24k-magic"),
                timestamp=date,
                venue_name="Madison Square Garden",
                city=default_city,
                category=default_category,
                image_url="https://via.placeholder.com/300x200?text=Bruno+Mars",
                price_range="$180 - $600",
                min_price=180.0,
                max_price=600.0,
                currency="USD",
                scores={"popularity": 0.88},
                provider="viagogo",
                viagogo_url=self._build_viagogo_url("bruno-mars-24k-magic")
            ),
            EventMention(
                id="viagogo-2",
                text="The Weeknd - After Hours Tour",
                url=self._build_viagogo_url("the-weeknd-after-hours"),
                timestamp=date,
                venue_name="Barclays Center",
                city=default_city,
                category=default_category,
                image_url="https://via.placeholder.com/300x200?text=The+Weeknd",
                price_range="$95 - $450",
                min_price=95.0,
                max_price=450.0,
                currency="USD",
                scores={"popularity": 0.91},
                provider="viagogo",
                viagogo_url=self._build_viagogo_url("the-weeknd-after-hours")
            ),
            EventMention(
                id="viagogo-3",
                text="Adele - Weekends with Adele",
                url=self._build_viagogo_url("adele-weekends"),
                timestamp=date,
                venue_name="The Colosseum",
                city="Las Vegas" if not city else city,
                category=default_category,
                image_url="https://via.placeholder.com/300x200?text=Adele",
                price_range="$250 - $1200",
                min_price=250.0,
                max_price=1200.0,
                currency="USD",
                scores={"popularity": 0.96},
                provider="viagogo",
                viagogo_url=self._build_viagogo_url("adele-weekends")
            ),
        ]
        return events

    def _get_mock_artist_events(
        self,
        artist: str,
        date_from: Optional[str] = None
    ) -> List[EventMention]:
        """Return mock artist-specific events from Viagogo."""
        base_date = date_from or "2025-06-15"
        artist_slug = artist.lower().replace(" ", "-")
        
        return [
            EventMention(
                id=f"viagogo-artist-1",
                text=f"{artist} - The Chromatica Ball",
                url=self._build_viagogo_url(f"{artist_slug}-chromatica-ball"),
                timestamp=base_date,
                venue_name="O2 Arena",
                city="London",
                category="music",
                image_url="https://images.unsplash.com/photo-1459749411177-27352851d941?w=800&q=80",
                price_range="$120 - $550",
                min_price=120.0,
                max_price=550.0,
                currency="USD",
                scores={"popularity": 0.85},
                provider="viagogo",
                ticket_provider="viagogo",
                viagogo_url=self._build_viagogo_url(f"{artist_slug}-chromatica-ball")
            ),
            EventMention(
                id=f"viagogo-artist-2",
                text=f"{artist} - Las Vegas Residency",
                url=self._build_viagogo_url(f"{artist_slug}-vegas-residency"),
                timestamp=base_date,
                venue_name="Dolby Live",
                city="Las Vegas",
                category="music",
                image_url="https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=800&q=80",
                price_range="$250 - $800",
                min_price=250.0,
                max_price=800.0,
                currency="USD",
                scores={"popularity": 0.95},
                provider="viagogo",
                ticket_provider="viagogo",
                viagogo_url=self._build_viagogo_url(f"{artist_slug}-vegas-residency")
            )
        ]


# Singleton instance for backward-compatible access
_collector = ViagogoCollector()


async def search_viagogo_events(
    date: str,
    city: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20,
    country_code: str = "US"
) -> List[EventMention]:
    """Helper function to search Viagogo events."""
    query = EventSearchQuery(date, city, category, limit, country_code)
    return await _collector.search(query)

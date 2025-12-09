"""Events API routes."""
from fastapi import APIRouter, Query, Path, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode
from api.models.event import EventMention, EventPackageResponse, TicketsInfo, HotelsInfo
from api.collectors.ticketmaster import TicketmasterCollector
from api.services.collector import MultiCollector
from api.collectors.base import EventSearchQuery, ArtistSearchQuery
from api import config

router = APIRouter(prefix="/api", tags=["events"])

# Initialize MultiCollector with Ticketmaster as the primary provider
# Future: Inject this dependency or load from config
_multi_collector = MultiCollector(collectors=[TicketmasterCollector()])

# In-memory cache for events (simulates storage for package lookup)
_events_cache: dict[str, EventMention] = {}


def _cache_events(events: List[EventMention]) -> None:
    """Cache events for package lookup."""
    for event in events:
        _events_cache[event.id] = event


def _build_booking_url(city: str, check_in: str, check_out: str) -> str:
    """Build Booking.com affiliate search URL."""
    check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
    
    params = {
        "ss": city,
        "checkin_year": check_in_date.year,
        "checkin_month": check_in_date.month,
        "checkin_monthday": check_in_date.day,
        "checkout_year": check_out_date.year,
        "checkout_month": check_out_date.month,
        "checkout_monthday": check_out_date.day,
        "aid": config.BOOKING_AFFILIATE_ID
    }
    
    return f"{config.BOOKING_BASE_URL}?{urlencode(params)}"


@router.get("/events", response_model=List[EventMention])
async def search_events(
    date: str = Query(
        ...,
        description="Event date in YYYY-MM-DD format (required)",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    ),
    city: Optional[str] = Query(
        default=None,
        description="City name (e.g., 'Tel Aviv'). Optional filter."
    ),
    category: Optional[str] = Query(
        default=None,
        description="Event category: music, sports, arts, family. Optional filter."
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Max events to return"),
    country_code: str = Query(
        default=config.DEFAULT_COUNTRY_CODE,
        description="Country code (e.g., 'IL', 'US')"
    ),
    page: int = Query(default=0, ge=0, description="Page number (0-indexed)")
) -> List[EventMention]:
    """
    Search for events by date with optional city and category filters.
    
    Returns a list of events with affiliate ticket URLs for monetization.
    """
    query = EventSearchQuery(
        date=date,
        city=city,
        category=category,
        limit=limit,
        country_code=country_code,
        page=page
    )
    events = await _multi_collector.search(query)
    _cache_events(events)
    return events


@router.get("/events/by-artist", response_model=List[EventMention])
async def search_events_by_artist(
    artist: str = Query(
        ...,
        description="Artist or performer name to search for (required)"
    ),
    date_from: Optional[str] = Query(
        default=None,
        description="Start date in YYYY-MM-DD format. Optional.",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    ),
    date_to: Optional[str] = Query(
        default=None,
        description="End date in YYYY-MM-DD format. Optional.",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    ),
    country_code: str = Query(
        default="US",
        description="Country code (e.g., 'US', 'GB', 'IL')"
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Max events to return"),
    page: int = Query(default=0, ge=0, description="Page number (0-indexed)")
) -> List[EventMention]:
    """
    Search for events by artist/performer name.
    
    Returns a list of upcoming events for the specified artist with affiliate ticket URLs.
    """
    query = ArtistSearchQuery(
        artist=artist,
        date_from=date_from,
        date_to=date_to,
        country_code=country_code,
        limit=limit,
        page=page
    )
    events = await _multi_collector.search_by_artist(query)
    _cache_events(events)
    return events


@router.get("/events/{event_id}/package", response_model=EventPackageResponse)
async def get_event_package(
    event_id: str = Path(..., description="Ticketmaster event ID"),
    origin_city: Optional[str] = Query(
        default=None,
        description="Origin city for flights (for future use)"
    )
) -> EventPackageResponse:
    """
    Get a package for an event including tickets and hotel links.
    
    Returns event details with affiliate URLs for tickets and hotels.
    """
    # Try to find event in cache
    event = _events_cache.get(event_id)
    
    if not event:
        # Return mock event for demo purposes if not in cache
        event = EventMention(
            id=event_id,
            text="Event Package Demo",
            url="https://www.ticketmaster.com/",
            timestamp=datetime.now().strftime("%Y-%m-%d"),
            venue_name="Demo Venue",
            city="New York",
            category="music"
        )
    
    # Calculate check-in/check-out dates
    event_date = datetime.strptime(event.timestamp, "%Y-%m-%d")
    check_in = event.timestamp
    check_out = (event_date + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Build response
    tickets = TicketsInfo(url=event.url)
    hotels = HotelsInfo(
        city=event.city,
        check_in=check_in,
        check_out=check_out,
        affiliate_url=_build_booking_url(event.city, check_in, check_out)
    )
    
    return EventPackageResponse(
        event=event,
        tickets=tickets,
        hotels=hotels
    )

# -*- coding: utf-8 -*-
"""Events API routes."""
from fastapi import APIRouter, Query, Path, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode
from api.models.event import EventMention, EventPackageResponse, TicketsInfo, HotelsInfo
from api.collectors.ticketmaster import TicketmasterCollector
from api.collectors.viagogo import ViagogoCollector
from api.services.collector import MultiCollector
from api.collectors.base import EventSearchQuery, ArtistSearchQuery
from api import config

router = APIRouter(prefix="/api", tags=["events"])

# Initialize MultiCollector with Viagogo first (priority), then Ticketmaster (fallback)
# Order matters: first collector in list has highest priority
_multi_collector = MultiCollector(collectors=[
    ViagogoCollector(),     # Primary: Viagogo for event discovery
    TicketmasterCollector() # Fallback: Ticketmaster if Viagogo returns empty
])

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


def _determine_ticket_info(event: EventMention) -> TicketsInfo:
    """
    Determine the best ticket source based on provider priority.
    
    Priority order:
    1. Ticketmaster URL -> ticket_provider="ticketmaster"
    2. Official site URL -> ticket_provider="official_site" (future)
    3. Viagogo URL -> ticket_provider="viagogo" (with affiliate)
    4. None -> no tickets available
    """
    # Priority 1: If event has a Ticketmaster URL
    if event.provider == "ticketmaster" and event.url:
        return TicketsInfo(
            url=event.url,
            ticket_provider="ticketmaster"
        )
    
    # Priority 2: Official site URL (placeholder for future WebSearchCollector)
    # TODO: Check for official_site_url field when available
    # if event.official_site_url:
    #     return TicketsInfo(url=event.official_site_url, ticket_provider="official_site")
    
    # Priority 3: Viagogo URL as fallback
    if event.viagogo_url:
        # Viagogo URL already includes affiliate ID from collector
        return TicketsInfo(
            url=event.viagogo_url,
            ticket_provider="viagogo"
        )
    
    # If we have any URL at all (e.g., from Viagogo provider), use it
    if event.url:
        # Determine provider based on URL or event.provider
        if "viagogo" in event.url.lower():
            return TicketsInfo(
                url=event.url,
                ticket_provider="viagogo"
            )
        elif "ticketmaster" in event.url.lower():
            return TicketsInfo(
                url=event.url,
                ticket_provider="ticketmaster"
            )
        else:
            return TicketsInfo(
                url=event.url,
                ticket_provider=event.provider
            )
    
    # Priority 4: No tickets available
    return TicketsInfo(url=None, ticket_provider=None)


@router.get("/events/{event_id}/package", response_model=EventPackageResponse)
async def get_event_package(
    event_id: str = Path(..., description="Event ID from any provider"),
    origin_city: Optional[str] = Query(
        default=None,
        description="Origin city for flights (for future use)"
    )
) -> EventPackageResponse:
    """
    Get a package for an event including tickets and hotel links.
    
    Returns event details with affiliate URLs for tickets and hotels.
    Ticket provider is determined by priority: Ticketmaster -> Official site -> Viagogo.
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
            category="music",
            provider="ticketmaster"
        )
    
    # Calculate check-in/check-out dates
    event_date = datetime.strptime(event.timestamp, "%Y-%m-%d")
    check_in = event.timestamp
    check_out = (event_date + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Determine ticket source using priority logic
    tickets = _determine_ticket_info(event)
    
    # Update event's ticket_provider for consistency
    event_with_ticket_provider = event.model_copy(update={
        "ticket_provider": tickets.ticket_provider
    })
    
    # Build hotel info
    hotels = HotelsInfo(
        city=event.city,
        check_in=check_in,
        check_out=check_out,
        affiliate_url=_build_booking_url(event.city, check_in, check_out)
    )
    
    return EventPackageResponse(
        event=event_with_ticket_provider,
        tickets=tickets,
        hotels=hotels
    )

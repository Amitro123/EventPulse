"""EventPulse data models."""
from pydantic import BaseModel
from typing import Optional


class EventMention(BaseModel):
    """Event model representing a Ticketmaster event."""
    id: str
    text: str  # Event name, e.g., "Coldplay - Music of the Spheres"
    url: str  # Affiliate ticket link
    timestamp: str  # Event date
    venue_name: str
    city: str
    category: Optional[str] = None
    image_url: Optional[str] = None
    price_range: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    currency: Optional[str] = None
    venue_lat: Optional[float] = None
    venue_lng: Optional[float] = None
    scores: dict = {}  # Analyzer output (popularity, etc.)
    raw_data: Optional[dict] = None
    provider: str = "ticketmaster"


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str


class EventSearchRequest(BaseModel):
    """Request model for event search."""
    date: str
    city: str
    category: str = "music"
    limit: int = 20


class TicketsInfo(BaseModel):
    """Ticket information for package."""
    url: str


class HotelsInfo(BaseModel):
    """Hotel information for package with affiliate link."""
    city: str
    check_in: str  # YYYY-MM-DD
    check_out: str  # YYYY-MM-DD
    affiliate_url: str


class EventPackageResponse(BaseModel):
    """Package response combining event, tickets, and hotels."""
    event: EventMention
    tickets: TicketsInfo
    hotels: HotelsInfo


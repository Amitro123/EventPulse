from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from api.models.event import EventMention

@dataclass
class EventSearchQuery:
    date: str
    city: Optional[str] = None
    category: Optional[str] = None
    limit: int = 20
    country_code: str = "IL"
    page: int = 0

@dataclass
class ArtistSearchQuery:
    artist: str
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    country_code: str = "US"
    limit: int = 20
    page: int = 0

class EventCollector(ABC):
    """Abstract base class for event collectors."""

    @abstractmethod
    async def search(self, query: EventSearchQuery) -> List[EventMention]:
        """Search events by date/location."""
        pass

    @abstractmethod
    async def search_by_artist(self, query: ArtistSearchQuery) -> tuple[List[EventMention], int]:
        """Search events by artist. Returns (events, total_count)."""
        pass

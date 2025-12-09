
import pytest
from unittest.mock import AsyncMock, MagicMock
from api.services.collector import MultiCollector
from api.collectors.base import EventCollector, EventSearchQuery, ArtistSearchQuery
from api.models.event import EventMention

class MockCollector(EventCollector):
    """Mock collector for testing."""
    def __init__(self, name: str, events: list = None, artist_events: list = None):
        self.name = name
        self.events = events or []
        self.artist_events = artist_events or []

    async def search(self, query: EventSearchQuery):
        return self.events

    async def search_by_artist(self, query: ArtistSearchQuery):
        return self.artist_events

@pytest.mark.asyncio
async def test_multicollector_aggregation():
    """Test that MultiCollector aggregates events from multiple collectors."""
    # Setup mock events
    event1 = EventMention(id="1", text="Event 1", url="http://1", timestamp="2025-01-01", venue_name="V1", city="C1", provider="mock1")
    event2 = EventMention(id="2", text="Event 2", url="http://2", timestamp="2025-01-01", venue_name="V2", city="C2", provider="mock2")
    
    c1 = MockCollector("c1", events=[event1])
    c2 = MockCollector("c2", events=[event2])
    
    service = MultiCollector(collectors=[c1, c2])
    
    query = EventSearchQuery(date="2025-01-01")
    events = await service.search(query)
    
    assert len(events) == 2
    assert events[0].provider == "mock1"
    assert events[1].provider == "mock2"

@pytest.mark.asyncio
async def test_multicollector_error_handling():
    """Test that MultiCollector continues if one collector fails."""
    # Setup successful mock event
    event1 = EventMention(id="1", text="Event 1", url="http://1", timestamp="2025-01-01", venue_name="V1", city="C1", provider="mock1")
    c1 = MockCollector("c1", events=[event1])
    
    # Setup failing collector
    c2 = MagicMock(spec=EventCollector)
    c2.search = AsyncMock(side_effect=Exception("API Error"))
    
    service = MultiCollector(collectors=[c1, c2])
    
    query = EventSearchQuery(date="2025-01-01")
    events = await service.search(query)
    
    # Should still get results from c1
    assert len(events) == 1
    assert events[0].id == "1"

@pytest.mark.asyncio
async def test_artist_search_aggregation():
    """Test artist search aggregation."""
    event1 = EventMention(id="a1", text="Artist Event 1", url="http://1", timestamp="2025-01-01", venue_name="V1", city="C1", provider="mock1")
    c1 = MockCollector("c1", artist_events=[event1])
    
    service = MultiCollector(collectors=[c1])
    
    query = ArtistSearchQuery(artist="Test Artist")
    events = await service.search_by_artist(query)
    
    assert len(events) == 1
    assert events[0].text == "Artist Event 1"

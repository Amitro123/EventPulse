
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
        self.search_called = False
        self.search_by_artist_called = False

    async def search(self, query: EventSearchQuery):
        self.search_called = True
        return self.events

    async def search_by_artist(self, query: ArtistSearchQuery):
        self.search_by_artist_called = True
        return self.artist_events

@pytest.mark.asyncio
async def test_multicollector_aggregation():
    """Test that MultiCollector uses priority-based fallback (not aggregation)."""
    # Setup mock events
    event1 = EventMention(id="1", text="Event 1", url="http://1", timestamp="2025-01-01", venue_name="V1", city="C1", provider="mock1")
    event2 = EventMention(id="2", text="Event 2", url="http://2", timestamp="2025-01-01", venue_name="V2", city="C2", provider="mock2")
    
    c1 = MockCollector("c1", events=[event1])
    c2 = MockCollector("c2", events=[event2])
    
    service = MultiCollector(collectors=[c1, c2])
    
    query = EventSearchQuery(date="2025-01-01")
    events = await service.search(query)
    
    # With priority fallback, only first collector with results is used
    assert len(events) == 1
    assert events[0].provider == "mock1"
    # Second collector should NOT be called
    assert c2.search_called is False

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


# =========================================
# Tests for MultiCollector Priority Logic
# =========================================

@pytest.mark.asyncio
async def test_multicollector_viagogo_first_priority():
    """Test that Viagogo is tried first and Ticketmaster is NOT called when Viagogo has results."""
    viagogo_event = EventMention(
        id="vg-1", 
        text="Viagogo Event", 
        url="http://viagogo.com/e1", 
        timestamp="2025-01-01", 
        venue_name="V1", 
        city="C1", 
        provider="viagogo"
    )
    ticketmaster_event = EventMention(
        id="tm-1", 
        text="Ticketmaster Event", 
        url="http://ticketmaster.com/e1", 
        timestamp="2025-01-01", 
        venue_name="V2", 
        city="C2", 
        provider="ticketmaster"
    )
    
    viagogo_collector = MockCollector("viagogo", events=[viagogo_event])
    ticketmaster_collector = MockCollector("ticketmaster", events=[ticketmaster_event])
    
    # Viagogo is first in priority order
    service = MultiCollector(collectors=[viagogo_collector, ticketmaster_collector])
    
    query = EventSearchQuery(date="2025-01-01")
    events = await service.search(query)
    
    # Should only get Viagogo events (priority fallback stops at first success)
    assert len(events) == 1, f"Expected 1 event, got {len(events)}"
    assert events[0].provider == "viagogo"
    assert events[0].id == "vg-1"
    
    # Viagogo was called, Ticketmaster was NOT called
    assert viagogo_collector.search_called is True
    assert ticketmaster_collector.search_called is False


@pytest.mark.asyncio
async def test_multicollector_fallback_to_ticketmaster():
    """Test that Ticketmaster is used when Viagogo returns empty."""
    ticketmaster_event = EventMention(
        id="tm-1", 
        text="Ticketmaster Event", 
        url="http://ticketmaster.com/e1", 
        timestamp="2025-01-01", 
        venue_name="V2", 
        city="C2", 
        provider="ticketmaster"
    )
    
    # Viagogo returns empty, Ticketmaster returns data
    viagogo_collector = MockCollector("viagogo", events=[])
    ticketmaster_collector = MockCollector("ticketmaster", events=[ticketmaster_event])
    
    service = MultiCollector(collectors=[viagogo_collector, ticketmaster_collector])
    
    query = EventSearchQuery(date="2025-01-01")
    events = await service.search(query)
    
    # Should fall back to Ticketmaster events
    assert len(events) == 1
    assert events[0].provider == "ticketmaster"
    assert events[0].id == "tm-1"
    
    # Both collectors were called due to fallback
    assert viagogo_collector.search_called is True
    assert ticketmaster_collector.search_called is True


@pytest.mark.asyncio
async def test_multicollector_artist_search_priority():
    """Test priority fallback for artist search."""
    viagogo_event = EventMention(
        id="vg-artist-1", 
        text="Artist on Viagogo", 
        url="http://viagogo.com/artist", 
        timestamp="2025-01-01", 
        venue_name="V1", 
        city="C1", 
        provider="viagogo"
    )
    
    viagogo_collector = MockCollector("viagogo", artist_events=[viagogo_event])
    ticketmaster_collector = MockCollector("ticketmaster", artist_events=[])
    
    service = MultiCollector(collectors=[viagogo_collector, ticketmaster_collector])
    
    query = ArtistSearchQuery(artist="Test Artist")
    events = await service.search_by_artist(query)
    
    # Should get Viagogo artist events (priority fallback)
    assert len(events) == 1
    assert events[0].provider == "viagogo"
    # Ticketmaster should NOT be called since Viagogo returned results
    assert viagogo_collector.search_by_artist_called is True
    assert ticketmaster_collector.search_by_artist_called is False


@pytest.mark.asyncio
async def test_multicollector_error_fallback():
    """Test that collector errors trigger fallback to next collector."""
    ticketmaster_event = EventMention(
        id="tm-1", 
        text="Ticketmaster Event", 
        url="http://ticketmaster.com/e1", 
        timestamp="2025-01-01", 
        venue_name="V2", 
        city="C2", 
        provider="ticketmaster"
    )
    
    # Viagogo raises an error
    failing_collector = MagicMock(spec=EventCollector)
    failing_collector.search = AsyncMock(side_effect=Exception("Viagogo API Error"))
    
    ticketmaster_collector = MockCollector("ticketmaster", events=[ticketmaster_event])
    
    service = MultiCollector(collectors=[failing_collector, ticketmaster_collector])
    
    query = EventSearchQuery(date="2025-01-01")
    events = await service.search(query)
    
    # Should fall back to Ticketmaster
    assert len(events) == 1
    assert events[0].provider == "ticketmaster"


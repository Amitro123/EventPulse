from typing import List, Dict
import logging
from api.collectors.base import EventCollector, EventSearchQuery, ArtistSearchQuery
from api.models.event import EventMention

# Configure logger
logger = logging.getLogger(__name__)

class MultiCollector:
    """Service to orchestrate multiple event collectors."""

    def __init__(self, collectors: List[EventCollector]):
        self.collectors = collectors

    async def search(self, query: EventSearchQuery) -> List[EventMention]:
        """
        Search for events across all registered collectors.
        For now, returns results from the first successful collector.
        """
        all_events = []
        for collector in self.collectors:
            try:
                # Log usage
                provider_name = collector.__class__.__name__
                events = await collector.search(query)
                
                if events:
                    count = len(events)
                    logger.info(f"Collected {count} events from {provider_name}")
                    # For Phase 3 Step 1, we can just aggregate or return first match.
                    # Given the roadmap implies fallback logic: "Try Ticketmaster -> if no result... query Viagogo"
                    # But for generic search we might want to aggregate.
                    # Let's aggregate for now to support multi-source.
                    all_events.extend(events)
                    
                    # If we have enough events, we could stop. But for now collect all.
            except Exception as e:
                logger.error(f"Error collecting from {collector.__class__.__name__}: {e}")
        
        return all_events

    async def search_by_artist(self, query: ArtistSearchQuery) -> List[EventMention]:
        """Search by artist across all collectors."""
        all_events = []
        for collector in self.collectors:
            try:
                provider_name = collector.__class__.__name__
                events = await collector.search_by_artist(query)
                
                if events:
                    count = len(events)
                    logger.info(f"Collected {count} artist events from {provider_name}")
                    all_events.extend(events)
            except Exception as e:
                logger.error(f"Error collecting artist events from {collector.__class__.__name__}: {e}")
                
        return all_events

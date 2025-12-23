# -*- coding: utf-8 -*-
"""Multi-collector service for orchestrating event collectors."""
from typing import List, Dict
import logging
from api.collectors.base import EventCollector, EventSearchQuery, ArtistSearchQuery
from api.models.event import EventMention

# Configure logger
logger = logging.getLogger(__name__)


class MultiCollector:
    """
    Service to orchestrate multiple event collectors with priority-based fallback.
    
    Priority order: Viagogo first, then Ticketmaster fallback.
    Stops on first collector that returns results.
    """

    def __init__(self, collectors: List[EventCollector]):
        """
        Initialize with list of collectors in priority order.
        First collector in the list has highest priority.
        """
        self.collectors = collectors

    async def search(self, query: EventSearchQuery) -> List[EventMention]:
        """
        Search for events using priority-based fallback.
        
        Tries each collector in order until one returns results.
        If a collector fails or returns empty, moves to next.
        """
        for collector in self.collectors:
            provider_name = collector.__class__.__name__
            try:
                logger.info(f"Trying {provider_name} for event search...")
                events = await collector.search(query)
                
                if events:
                    count = len(events)
                    logger.info(f"Got {count} events from {provider_name} - using these results")
                    return events
                else:
                    logger.info(f"{provider_name} returned no events, trying next collector...")
                    
            except Exception as e:
                logger.error(f"Error collecting from {provider_name}: {e}")
                logger.info(f"Falling back to next collector...")
        
        logger.warning("All collectors returned empty results")
        return []

    async def search_by_artist(self, query: ArtistSearchQuery) -> List[EventMention]:
        """
        Search by artist using priority-based fallback.
        
        Same logic as search(): tries collectors in order, 
        returns results from first successful one.
        """
        for collector in self.collectors:
            provider_name = collector.__class__.__name__
            try:
                logger.info(f"Trying {provider_name} for artist search: {query.artist}")
                events = await collector.search_by_artist(query)
                
                if events:
                    count = len(events)
                    logger.info(f"Got {count} artist events from {provider_name} - using these results")
                    return events
                else:
                    logger.info(f"{provider_name} returned no artist events, trying next collector...")
                    
            except Exception as e:
                logger.error(f"Error collecting artist events from {provider_name}: {e}")
                logger.info(f"Falling back to next collector...")
        
        logger.warning(f"All collectors returned empty results for artist: {query.artist}")
        return []

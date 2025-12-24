
import pytest
from unittest.mock import patch, AsyncMock, Mock
from api.collectors.ticketmaster import TicketmasterCollector, EventSearchQuery
from api.models.event import EventMention

@pytest.mark.asyncio
async def test_reproduce_ticketmaster_missing_url():
    """
    Reproduction test for when Ticketmaster API returns an event without a 'url' field.
    The collector should fallback to constructing a valid URL using the event ID.
    """
    # Mock response without 'url' field and verify we reconstruct it
    mock_response = {
        "_embedded": {
            "events": [
                {
                    "id": "Za5ju3rKuqZBSr8F1YJAkMtDVh1SMahv3",
                    "name": "Event Without URL",
                    # "url": "..." # MISSING
                    "dates": {
                        "start": {"localDate": "2025-12-15"},
                        "status": {"code": "onsale"}
                    },
                    "_embedded": {
                        "venues": [{"name": "Venue", "city": {"name": "City"}}]
                    },
                    "_links": {
                        "self": {"href": "/discovery/v2/events/Za5ju3rKuqZBSr8F1YJAkMtDVh1SMahv3"}
                    }
                }
            ]
        }
    }

    with patch("api.collectors.ticketmaster.config.TICKETMASTER_API_KEY", "test-key"):
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_response_obj = AsyncMock()
            mock_response_obj.status_code = 200
            mock_response_obj.json = Mock(return_value=mock_response)
            mock_response_obj.raise_for_status = Mock()
            
            mock_client = mock_client_cls.return_value
            mock_client.__aenter__.return_value = mock_client
            mock_client.get = AsyncMock(return_value=mock_response_obj)
            
            collector = TicketmasterCollector()
            query = EventSearchQuery(date="2025-12-15")
            events = await collector.search(query)
            
            assert len(events) == 1
            event = events[0]
            
            # This assertion fails if the bug exists (currently event.url would be "")
            print(f"DEBUG: Event URL is '{event.url}'")
            assert event.url and event.url.startswith("http"), "Event URL should be populated even if missing in API response"
            assert "ticketmaster.com" in event.url, "Event URL should point to Ticketmaster"
            assert event.id in event.url, "Event URL should contain the event ID"
            assert event.ticket_provider == "ticketmaster", "Ticket Provider should be ticketmaster"

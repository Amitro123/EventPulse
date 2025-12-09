"""Tests for EventPulse API."""
import os
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from api.main import app
from api.collectors.ticketmaster import collect_events, _get_mock_events


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_returns_ok(self):
        """Health endpoint should return status ok."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestEventsEndpoint:
    """Tests for events search endpoint."""
    
    @pytest.fixture(autouse=True)
    def mock_api_key(self):
        """Force mock mode for these tests."""
        with patch("api.config.TICKETMASTER_API_KEY", "test"):
            yield
    
    def test_events_requires_date(self):
        """Events endpoint should require date parameter."""
        response = client.get("/api/events?city=Tel%20Aviv")
        assert response.status_code == 422
    
    def test_events_with_date_only(self):
        """Events endpoint should work with only date (city/category optional)."""
        response = client.get("/api/events?date=2025-12-15")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Should return mock events
    
    def test_events_validates_date_format(self):
        """Events endpoint should validate date format."""
        response = client.get("/api/events?date=invalid")
        assert response.status_code == 422
    
    def test_events_returns_list(self):
        """Events endpoint should return a list."""
        response = client.get("/api/events?date=2025-12-15&city=Tel%20Aviv")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_events_with_all_params(self):
        """Events endpoint should accept all parameters."""
        response = client.get(
            "/api/events?date=2025-12-15&city=Tel%20Aviv&category=music&limit=10&country_code=IL"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestTicketmasterCollector:
    """Tests for Ticketmaster collector."""
    
    def test_mock_events_returns_data(self):
        """Mock events should return sample data."""
        events = _get_mock_events("2025-12-15", "Tel Aviv", "music")
        assert len(events) > 0
        assert events[0].id == "mock-1"
        assert "Coldplay" in events[0].text
    
    def test_mock_events_with_none_params(self):
        """Mock events should work with None city/category."""
        events = _get_mock_events("2025-12-15")
        assert len(events) > 0
        assert events[0].city == "Tel Aviv"  # Default city
        assert events[0].category == "music"  # Default category
    
    def test_mock_events_have_required_fields(self):
        """Mock events should have all required fields."""
        events = _get_mock_events("2025-12-15", "Tel Aviv", "music")
        for event in events:
            assert event.id
            assert event.text
            assert event.url
            assert event.timestamp
            assert event.venue_name
            assert event.city
    
    @pytest.mark.asyncio
    async def test_collect_events_without_api_key(self):
        """Collector should return mock data when no API key."""
        with patch("api.collectors.ticketmaster.config.TICKETMASTER_API_KEY", ""):
            events = await collect_events("2025-12-15", "Tel Aviv", "music")
            assert len(events) > 0
            # Should be mock data
            assert events[0].id.startswith("mock")
    
    @pytest.mark.asyncio
    async def test_collect_events_with_api_error(self):
        """Collector should handle API errors gracefully."""
        with patch("api.collectors.ticketmaster.config.TICKETMASTER_API_KEY", "test-key"):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = mock_client_cls.return_value
                mock_client.__aenter__.return_value = mock_client
                # client.get must be awaitable
                mock_client.get = AsyncMock(side_effect=Exception("API Error"))
                
                events = await collect_events("2025-12-15", "Tel Aviv", "music")
                # Should return empty list on error
                assert events == []

    @pytest.mark.asyncio
    async def test_parsing_price_and_location(self):
        """Collector should correctly parse price ranges and venue location."""
        mock_response = {
            "_embedded": {
                "events": [
                    {
                        "id": "test-1",
                        "name": "Test Event",
                        "url": "http://ticketmaster.com/event/1",
                        "dates": {"start": {"localDate": "2025-12-15"}},
                        "priceRanges": [
                            {"min": 50.0, "max": 150.0, "currency": "USD"}
                        ],
                        "_embedded": {
                            "venues": [
                                {
                                    "name": "Test Venue",
                                    "city": {"name": "Test City"},
                                    "location": {"latitude": "34.05", "longitude": "-118.25"}
                                }
                            ]
                        }
                    }
                ]
            }
        }

        with patch("api.collectors.ticketmaster.config.TICKETMASTER_API_KEY", "test-key"):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = mock_client_cls.return_value
                mock_client.__aenter__.return_value = mock_client
                mock_client.get = AsyncMock()
                mock_client.get.return_value.status_code = 200
                mock_client.get.return_value.json.return_value = mock_response
                
                events = await collect_events("2025-12-15", "Test City")
                
                assert len(events) == 1
                e = events[0]
                assert e.min_price == 50.0
                assert e.max_price == 150.0
                assert e.currency == "USD"
                assert e.venue_lat == 34.05
                assert e.venue_lng == -118.25
                assert e.price_range == "$50 - $150"

    @pytest.mark.asyncio
    async def test_parsing_missing_fields_gracefully(self):
        """Collector should handle missing price/location fields gracefully."""
        mock_response = {
            "_embedded": {
                "events": [
                    {
                        "id": "test-2",
                        "name": "Event No Data",
                        "url": "http://example.com",
                        "dates": {"start": {"localDate": "2025-12-15"}},
                        # No priceRanges
                        "_embedded": {
                            "venues": [
                                {
                                    "name": "Venue No Loc",
                                    "city": {"name": "City"},
                                    # No location
                                }
                            ]
                        }
                    }
                ]
            }
        }

        with patch("api.collectors.ticketmaster.config.TICKETMASTER_API_KEY", "test-key"):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = mock_client_cls.return_value
                mock_client.__aenter__.return_value = mock_client
                mock_client.get = AsyncMock()
                mock_client.get.return_value.status_code = 200
                mock_client.get.return_value.json.return_value = mock_response
                
                events = await collect_events("2025-12-15")
                
                assert len(events) == 1
                e = events[0]
                assert e.min_price is None
                assert e.max_price is None
                assert e.venue_lat is None
                assert e.venue_lng is None


class TestByArtistEndpoint:
    """Tests for events by-artist search endpoint."""
    
    @pytest.fixture(autouse=True)
    def mock_api_key(self):
        """Force mock mode for these tests."""
        with patch("api.config.TICKETMASTER_API_KEY", "test"):
            yield
    
    def test_by_artist_requires_artist(self):
        """By-artist endpoint should require artist parameter."""
        response = client.get("/api/events/by-artist")
        assert response.status_code == 422
    
    def test_by_artist_with_artist_only(self):
        """By-artist endpoint should work with only artist param."""
        response = client.get("/api/events/by-artist?artist=Coldplay")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Should return mock artist events
        # Verify artist name is in event text
        assert any("Coldplay" in event["text"] for event in data)
    
    def test_by_artist_with_date_range(self):
        """By-artist endpoint should accept date range params."""
        response = client.get(
            "/api/events/by-artist?artist=Ed%20Sheeran&date_from=2025-01-01&date_to=2025-12-31"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_by_artist_validates_date_format(self):
        """By-artist endpoint should validate date formats."""
        response = client.get("/api/events/by-artist?artist=Test&date_from=invalid")
        assert response.status_code == 422
    
    def test_by_artist_with_all_params(self):
        """By-artist endpoint should accept all parameters."""
        response = client.get(
            "/api/events/by-artist?artist=Taylor%20Swift&date_from=2025-06-01&date_to=2025-12-31&country_code=US&limit=50"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestPackageEndpoint:
    """Tests for event package endpoint."""
    
    def test_package_returns_valid_structure(self):
        """Package endpoint should return event, tickets, and hotels."""
        # First search to populate cache
        client.get("/api/events?date=2025-12-15")
        
        response = client.get("/api/events/mock-1/package")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "event" in data
        assert "tickets" in data
        assert "hotels" in data
        
        # Verify tickets
        assert "url" in data["tickets"]
        assert data["tickets"]["url"].startswith("http")
        
        # Verify hotels
        assert "city" in data["hotels"]
        assert "check_in" in data["hotels"]
        assert "check_out" in data["hotels"]
        assert "affiliate_url" in data["hotels"]
    
    def test_package_hotels_url_contains_city(self):
        """Package hotels URL should contain event city."""
        # First search to populate cache
        client.get("/api/events?date=2025-12-15")
        
        response = client.get("/api/events/mock-1/package")
        data = response.json()
        
        # Booking URL should contain the city
        affiliate_url = data["hotels"]["affiliate_url"]
        assert "booking.com" in affiliate_url
        assert "ss=" in affiliate_url  # City parameter
    
    def test_package_hotels_url_contains_dates(self):
        """Package hotels URL should contain check-in/check-out dates."""
        # First search to populate cache
        client.get("/api/events?date=2025-12-15")
        
        response = client.get("/api/events/mock-1/package")
        data = response.json()
        
        affiliate_url = data["hotels"]["affiliate_url"]
        
        # Should contain date parameters
        assert "checkin_year=" in affiliate_url
        assert "checkin_month=" in affiliate_url
        assert "checkin_monthday=" in affiliate_url
        assert "checkout_year=" in affiliate_url
        assert "checkout_month=" in affiliate_url
        assert "checkout_monthday=" in affiliate_url
    
    def test_package_hotels_url_contains_affiliate_id(self):
        """Package hotels URL should contain affiliate ID."""
        # First search to populate cache
        client.get("/api/events?date=2025-12-15")
        
        response = client.get("/api/events/mock-1/package")
        data = response.json()
        
        affiliate_url = data["hotels"]["affiliate_url"]
        
        # Should contain aid parameter (TEST_AID or real affiliate ID)
        assert "aid=" in affiliate_url
    
    def test_package_checkout_is_day_after_checkin(self):
        """Package check-out should be one day after check-in."""
        from datetime import datetime, timedelta
        
        # First search to populate cache
        client.get("/api/events?date=2025-12-15")
        
        response = client.get("/api/events/mock-1/package")
        data = response.json()
        
        check_in = datetime.strptime(data["hotels"]["check_in"], "%Y-%m-%d")
        check_out = datetime.strptime(data["hotels"]["check_out"], "%Y-%m-%d")
        
        assert check_out == check_in + timedelta(days=1)
    
    def test_package_with_unknown_event_returns_demo(self):
        """Package with unknown event ID should return demo data."""
        response = client.get("/api/events/unknown-event-id/package")
        assert response.status_code == 200
        data = response.json()
        
        # Should still have valid structure
        assert "event" in data
        assert "tickets" in data
        assert "hotels" in data
    
    def test_package_accepts_origin_city_param(self):
        """Package endpoint should accept optional origin_city param."""
        response = client.get("/api/events/mock-1/package?origin_city=New%20York")
        assert response.status_code == 200


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_returns_info(self):
        """Root endpoint should return API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "EventPulse" in str(data)


class TestLiveIntegration:
    """Live integration tests for Ticketmaster API."""
    
    @pytest.mark.skipif(
        not os.getenv("USE_TICKETMASTER_LIVE"),
        reason="Skipping live API tests unless USE_TICKETMASTER_LIVE is set"
    )
    @pytest.mark.asyncio
    async def test_live_ticketmaster_search(self):
        """Should fetch real events from Ticketmaster."""
        # Ensure we have a valid key in env before running
        events = await collect_events(
            date="2025-12-15",
            country_code="US",
            limit=5
        )
        
        # We expect some result or at least a graceful empty list
        assert isinstance(events, list)
        if len(events) > 0:
            e = events[0]
            assert e.id
            assert e.text
            assert e.url.startswith("http")
            print(f"Live event found: {e.text} at {e.venue_name}")

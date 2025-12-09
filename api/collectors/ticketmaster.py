"""Ticketmaster API collector for event discovery."""
import httpx
from typing import List, Optional
from api.models.event import EventMention
from api import config


async def collect_events(
    date: str,
    city: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20,
    country_code: str = "IL",
    page: int = 0
) -> List[EventMention]:
    """
    Collect events from Ticketmaster Discovery API.
    
    Args:
        date: Event date in YYYY-MM-DD format
        city: Optional city name (e.g., "Tel Aviv")
        category: Optional event category (music, sports, arts, etc.)
        limit: Maximum number of events to return
        country_code: Country code (default: IL for Israel)
        page: Page number (default: 0)
    
    Returns:
        List of EventMention objects with affiliate ticket links
    """
    # Check if API key is missing or is a placeholder value
    api_key = config.TICKETMASTER_API_KEY
    is_placeholder = not api_key or api_key.startswith("your_") or api_key == "test"
    
    if is_placeholder:
        # Return mock data for demo/testing without valid API key
        print("[INFO] Mock Mode: No valid Ticketmaster API key configured")
        return _get_mock_events(date, city, category)
    
    url = f"{config.TICKETMASTER_BASE_URL}/events.json"
    params = {
        "apikey": config.TICKETMASTER_API_KEY,
        "countryCode": country_code,
        "localStartDateTime": f"{date}T00:00:00,{date}T23:59:59",
        "size": limit,
        "sort": "date,asc",
        "page": page
    }
    
    # Add optional filters only if provided
    if city:
        params["city"] = city
    if category:
        params["classificationName"] = category
    
    events: List[EventMention] = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print(f"[INFO] Fetching events from Ticketmaster: date={date}, city={city}, country={country_code}")
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            # Log success
            print(f"[INFO] Ticketmaster Success: {response.status_code}")
            
            data = response.json()
            
            if "_embedded" not in data or "events" not in data["_embedded"]:
                print("[INFO] Ticketmaster: No events found")
                return events
            
            for e in data["_embedded"]["events"]:
                # Extract venue info safely
                venue_name = "TBA"
                event_city = city
                if "_embedded" in e and "venues" in e["_embedded"] and e["_embedded"]["venues"]:
                    venue = e["_embedded"]["venues"][0]
                    venue_name = venue.get("name", "TBA")
                    if "city" in venue:
                        event_city = venue["city"].get("name", city)
                
                # Extract price range
                price_range = None
                if "priceRanges" in e and e["priceRanges"]:
                    pr = e["priceRanges"][0]
                    price_range = f"${pr.get('min', 0):.0f} - ${pr.get('max', 0):.0f}"
                
                # Extract image
                image_url = None
                if "images" in e and e["images"]:
                    # Get the largest image
                    images = sorted(e["images"], key=lambda x: x.get("width", 0), reverse=True)
                    image_url = images[0].get("url")
                
                events.append(EventMention(
                    id=e["id"],
                    text=e.get("name", "Unknown Event"),
                    url=e.get("url", ""),  # Affiliate ticket link, safe get
                    timestamp=e.get("dates", {}).get("start", {}).get("localDate", date),
                    venue_name=venue_name,
                    city=event_city,
                    category=category,
                    image_url=image_url,
                    price_range=price_range,
                    scores={"popularity": e.get("score", 0)},
                    raw_data=e
                ))
                
        except httpx.HTTPStatusError as e:
            print(f"[ERROR] Ticketmaster API error: {e.response.status_code} - {e.response.text[:100]}")
        except Exception as e:
            print(f"[ERROR] Error fetching events: {e}")
    
    return events


def _get_mock_events(
    date: str,
    city: Optional[str] = None,
    category: Optional[str] = None
) -> List[EventMention]:
    """Return mock events for demo/testing when no API key is configured."""
    default_city = city or "Tel Aviv"
    default_category = category or "music"
    
    return [
        EventMention(
            id="mock-1",
            text="Coldplay - Music of the Spheres World Tour",
            url="https://www.ticketmaster.com/coldplay-tickets/artist/806431",
            timestamp=date,
            venue_name="Bloomfield Stadium",
            city=default_city,
            category=default_category,
            image_url="https://via.placeholder.com/300x200?text=Coldplay",
            price_range="$150 - $450",
            scores={"popularity": 0.95}
        ),
        EventMention(
            id="mock-2",
            text="Ed Sheeran - Mathematics Tour",
            url="https://www.ticketmaster.com/ed-sheeran-tickets/artist/1616239",
            timestamp=date,
            venue_name="Yarkon Park",
            city=default_city,
            category=default_category,
            image_url="https://via.placeholder.com/300x200?text=Ed+Sheeran",
            price_range="$120 - $380",
            scores={"popularity": 0.92}
        ),
        EventMention(
            id="mock-3",
            text="Maccabi Tel Aviv vs Hapoel Tel Aviv",
            url="https://www.ticketmaster.com/",
            timestamp=date,
            venue_name="Menora Mivtachim Arena",
            city=default_city,
            category="sports",
            image_url="https://via.placeholder.com/300x200?text=Basketball",
            price_range="$50 - $200",
            scores={"popularity": 0.88}
        ),
    ]


async def search_by_artist(
    artist: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    country_code: str = "US",
    limit: int = 20,
    page: int = 0
) -> List[EventMention]:
    """
    Search events by artist name using Ticketmaster Discovery API.
    
    Args:
        artist: Artist/performer name to search for (required)
        date_from: Optional start date in YYYY-MM-DD format
        date_to: Optional end date in YYYY-MM-DD format
        country_code: Country code (default: US)
        limit: Maximum number of events to return
        page: Page number (default: 0)
    
    Returns:
        List of EventMention objects with affiliate ticket links
    """
    # Check if API key is missing or is a placeholder value
    api_key = config.TICKETMASTER_API_KEY
    is_placeholder = not api_key or api_key.startswith("your_") or api_key == "test"
    
    if is_placeholder:
        print("[INFO] No valid Ticketmaster API key configured, using mock artist data")
        return _get_mock_artist_events(artist, date_from)
    
    url = f"{config.TICKETMASTER_BASE_URL}/events.json"
    params = {
        "apikey": config.TICKETMASTER_API_KEY,
        "keyword": artist,
        "countryCode": country_code,
        "size": limit,
        "sort": "date,asc",
        "page": page
    }
    
    # Add optional date range filters
    if date_from and date_to:
        params["localStartDateTime"] = f"{date_from}T00:00:00,{date_to}T23:59:59"
    elif date_from:
        params["localStartDateTime"] = f"{date_from}T00:00:00,*"
    elif date_to:
        params["localStartDateTime"] = f"*,{date_to}T23:59:59"
    
    events: List[EventMention] = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "_embedded" not in data or "events" not in data["_embedded"]:
                return events
            
            for e in data["_embedded"]["events"]:
                # Extract venue info safely
                venue_name = "TBA"
                event_city = "Unknown"
                if "_embedded" in e and "venues" in e["_embedded"] and e["_embedded"]["venues"]:
                    venue = e["_embedded"]["venues"][0]
                    venue_name = venue.get("name", "TBA")
                    if "city" in venue:
                        event_city = venue["city"].get("name", "Unknown")
                
                # Extract price range
                price_range = None
                if "priceRanges" in e and e["priceRanges"]:
                    pr = e["priceRanges"][0]
                    price_range = f"${pr.get('min', 0):.0f} - ${pr.get('max', 0):.0f}"
                
                # Extract image
                image_url = None
                if "images" in e and e["images"]:
                    images = sorted(e["images"], key=lambda x: x.get("width", 0), reverse=True)
                    image_url = images[0].get("url")
                
                # Extract category from classifications
                category = "music"
                if "classifications" in e and e["classifications"]:
                    category = e["classifications"][0].get("segment", {}).get("name", "music").lower()
                
                events.append(EventMention(
                    id=e["id"],
                    text=e["name"],
                    url=e["url"],
                    timestamp=e["dates"]["start"].get("localDate", ""),
                    venue_name=venue_name,
                    city=event_city,
                    category=category,
                    image_url=image_url,
                    price_range=price_range,
                    scores={"popularity": e.get("score", 0)},
                    raw_data=e
                ))
                
        except httpx.HTTPStatusError as e:
            print(f"Ticketmaster API error: {e.response.status_code}")
        except Exception as e:
            print(f"Error fetching events by artist: {e}")
    
    return events


def _get_mock_artist_events(artist: str, date_from: Optional[str] = None) -> List[EventMention]:
    """Return mock artist events for demo/testing when no API key is configured."""
    base_date = date_from or "2025-06-15"
    
    return [
        EventMention(
            id="artist-mock-1",
            text=f"{artist} - Live in Concert",
            url=f"https://www.ticketmaster.com/search?q={artist.replace(' ', '+')}",
            timestamp=base_date,
            venue_name="Madison Square Garden",
            city="New York",
            category="music",
            image_url=f"https://via.placeholder.com/300x200?text={artist.replace(' ', '+')}",
            price_range="$75 - $350",
            scores={"popularity": 0.90}
        ),
        EventMention(
            id="artist-mock-2",
            text=f"{artist} - World Tour",
            url=f"https://www.ticketmaster.com/search?q={artist.replace(' ', '+')}",
            timestamp=base_date,
            venue_name="O2 Arena",
            city="London",
            category="music",
            image_url=f"https://via.placeholder.com/300x200?text={artist.replace(' ', '+')}",
            price_range="$60 - $280",
            scores={"popularity": 0.88}
        ),
    ]


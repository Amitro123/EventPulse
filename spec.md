# EventPulse – Functional & Technical Spec

## 1. Product Overview

EventPulse is a web application that helps users discover concerts and sports events
by date, city, or artist, and then book full "packages" using affiliate links
for tickets, hotels, and flights.

**Primary use cases:**

1. "I have a date and a city – show me what's happening."
2. "I want to see a specific artist – show me where and when."
3. "Build a simple package around an event (tickets + hotel + flights)."

---

## 2. User Flows

### 2.1 Search by Date & City

1. User selects: date (required), city (optional), category (optional)
2. Frontend calls: `GET /api/events?date=YYYY-MM-DD&city=...&category=...`
3. Backend queries event sources with priority-based fallback:
   - **Viagogo** (primary) - tried first
   - **Ticketmaster** (fallback) - used if Viagogo returns no results
4. Returns list of events with `provider` field indicating source

### 2.2 Search by Artist

1. User enters: artist name (required), date range (optional)
2. Frontend calls: `GET /api/events/by-artist?artist=...&date_from=...&date_to=...`
3. Backend uses priority-based search (Viagogo → Ticketmaster)
4. Returns list of events for that artist with `provider` field

### 2.3 View Event Package

1. User clicks "View Package" on an event card
2. Frontend calls: `GET /api/events/{event_id}/package`
3. Backend determines best ticket source using priority:
   - **Ticketmaster** (preferred)
   - **Official site** (future)
   - **Viagogo** (fallback)
4. Modal displays:
   - Tickets section → link with "Tickets via [provider]" label
   - Hotels section → link to Booking.com (check-in = event date, check-out = event date + 1)

---

## 3. API Specification

### 3.1 GET /api/events

| Parameter | Required | Format | Description |
|-----------|----------|--------|-------------|
| `date` | ✅ | `YYYY-MM-DD` | Event date |
| `city` | No | String | City filter |
| `category` | No | String | music, sports, arts, family |
| `limit` | No | 1-100 | Max results (default: 20) |

### 3.2 GET /api/events/by-artist

| Parameter | Required | Format | Description |
|-----------|----------|--------|-------------|
| `artist` | ✅ | String | Artist/performer name |
| `date_from` | No | `YYYY-MM-DD` | Start date |
| `date_to` | No | `YYYY-MM-DD` | End date |
| `country_code` | No | String | ISO country code (default: US) |

### 3.3 GET /api/events/{event_id}/package

| Parameter | Required | Format | Description |
|-----------|----------|--------|-------------|
| `event_id` | ✅ (path) | String | Ticketmaster event ID |
| `origin_city` | No | String | Origin city (future: flights) |

**Response fields:**

- `event` – Full event object with `provider` and `ticket_provider` fields
- `tickets.url` – Ticket purchase URL (determined by priority)
- `tickets.ticket_provider` – Who sells the ticket ("ticketmaster", "viagogo", "official_site", or null)
- `hotels.city` – Event city
- `hotels.check_in` – Event date (YYYY-MM-DD)
- `hotels.check_out` – Event date + 1 day
- `hotels.affiliate_url` – Booking.com deep link with affiliate ID

**Ticket Provider Priority:**
1. Ticketmaster URL (constructed from event ID if missing in API response)
2. Official site URL (future feature)
3. Viagogo URL (if event from Viagogo or as fallback)
4. null (tickets unavailable or event cancelled)

---

## 4. Affiliate / Monetization

### 4.1 Supported Affiliates

| Provider | Integration | Revenue |
|----------|-------------|---------|
| **Ticketmaster** | Direct event URLs | Ticket sales commission |
| **Booking.com** | Affiliate deep links | Hotel booking commission |

### 4.2 Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `TICKETMASTER_API_KEY` | Discovery API access | (required) |
| `BOOKING_AFFILIATE_ID` | Booking.com partner ID | `TEST_AID` |

### 4.3 Booking.com URL Structure

```
https://www.booking.com/searchresults.html?
  ss={city}
  &checkin_year={YYYY}
  &checkin_month={MM}
  &checkin_monthday={DD}
  &checkout_year={YYYY}
  &checkout_month={MM}
  &checkout_monthday={DD}
  &aid={BOOKING_AFFILIATE_ID}
```

---

## 5. Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python 3.11+) |
| Frontend | React 18 |
| Styling | Vanilla CSS (dark theme) |
| External APIs | Ticketmaster Discovery API v2 |
| Deployment | Railway |

---

## 6. Data Models

### EventMention

```python
id: str              # Ticketmaster event ID
text: str            # Event name
url: str             # Ticket purchase URL
timestamp: str       # Event date (YYYY-MM-DD)
venue_name: str
city: str
category: Optional[str]
image_url: Optional[str]
price_range: Optional[str]
```

### EventPackageResponse

```python
event: EventMention
tickets: { url: str }
hotels: { city: str, check_in: str, check_out: str, affiliate_url: str }
```

# EventPulse

Event discovery platform for concerts and sports with affiliate monetization.

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file in project root:

```env
TICKETMASTER_API_KEY=your_ticketmaster_api_key
```

Get your API key from [Ticketmaster Developer Portal](https://developer.ticketmaster.com).

### 3. Using Live Ticketmaster Data

The application runs in **Mock Mode** by default if no API key is set. To use live data:

1.  Set `TICKETMASTER_API_KEY` in your `.env` file.
    - If the key starts with `your_` or is `test`, mock mode is used.
2.  Restart the backend server.

**Verify Live Data:**

Use the provided smoke test script:
```bash
python scripts/smoke_ticketmaster.py --country US --date 2025-12-15
```

Or verify with curl:
```bash
curl "http://localhost:8000/api/events?date=2025-12-15&country_code=US"
```

### 4. Run Development Servers

**Option A: Single command (recommended)**

```bash
# Install concurrently first (one time)
npm install

# Start both servers
npm run dev
```

**Option B: Batch file (Windows)**

```bash
# Opens backend and frontend in separate windows
dev.bat
```

**Option C: PowerShell script**

```powershell
# Runs both servers with colored output
.\dev.ps1
```

**Option D: Manual (separate terminals)**

```bash
# Terminal 1: Backend
.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000

# Terminal 2: Frontend  
cd src/ui/frontend && npm start
```

**Access:**
- 🔧 Backend API: http://localhost:8000
- 🎨 Frontend UI: http://localhost:3000
- 📚 API Docs: http://localhost:8000/docs

## API Endpoints

### Health Check

```bash
GET /api/health
```

Response: `{"status": "ok", "version": "1.0.0"}`

---

### Search by Date & City

Search events on a specific date with optional city and category filters.

```bash
GET /api/events?date=YYYY-MM-DD[&city=...][&category=...][&limit=N]
```

| Parameter | Required | Format | Description |
|-----------|----------|--------|-------------|
| `date` | ✅ Yes | `YYYY-MM-DD` | Event date |
| `city` | Optional | String | City name (e.g., "Tel Aviv", "New York") |
| `category` | Optional | String | `music`, `sports`, `arts`, `family` |
| `limit` | Optional | 1-100 | Max events to return (default: 20) |
| `country_code` | Optional | String | ISO country code (default: "IL") |

**Examples:**

```bash
# Date only
GET /api/events?date=2025-06-15

# Date + City
GET /api/events?date=2025-06-15&city=Tel%20Aviv

# All filters
GET /api/events?date=2025-06-15&city=New%20York&category=music&limit=10
```

---

### Search by Artist

Find events for a specific artist/performer.

```bash
GET /api/events/by-artist?artist=NAME[&date_from=...][&date_to=...][&country_code=...]
```

| Parameter | Required | Format | Description |
|-----------|----------|--------|-------------|
| `artist` | ✅ Yes | String | Artist/performer name |
| `date_from` | Optional | `YYYY-MM-DD` | Start date for search range |
| `date_to` | Optional | `YYYY-MM-DD` | End date for search range |
| `country_code` | Optional | String | ISO country code (default: "US") |
| `limit` | Optional | 1-100 | Max events to return (default: 20) |

**Examples:**

```bash
# Artist only
GET /api/events/by-artist?artist=Coldplay

# Artist with date range
GET /api/events/by-artist?artist=Taylor%20Swift&date_from=2025-01-01&date_to=2025-12-31

# Artist in specific country
GET /api/events/by-artist?artist=Ed%20Sheeran&country_code=GB&limit=10
```

---

### Event Package (Tickets + Hotels)

Get a package for an event with affiliate links for tickets and hotels.

```bash
GET /api/events/{event_id}/package[?origin_city=...]
```

| Parameter | Required | Format | Description |
|-----------|----------|--------|-------------|
| `event_id` | ✅ Yes (path) | String | Ticketmaster event ID |
| `origin_city` | Optional | String | Origin city for flights (future use) |

**Example Request:**

```bash
GET /api/events/tm_123/package
```

**Example Response:**

```json
{
  "event": { "id": "tm_123", "text": "Coldplay - Live", "city": "Tel Aviv", ... },
  "tickets": { "url": "https://ticketmaster.com/..." },
  "hotels": {
    "city": "Tel Aviv",
    "check_in": "2025-06-15",
    "check_out": "2025-06-16",
    "affiliate_url": "https://booking.com/searchresults.html?ss=Tel+Aviv&..."
  }
}
```

---

### Swagger UI

Interactive API docs available at: `http://localhost:8000/docs`


## Package API and Affiliate Links

### How to Use

1. **Search events** → Use "Search by Date" or "Search by Artist" tabs
2. **View package** → Click "📦 View Package" on any event card
3. **Book** → Click "Open Tickets" for Ticketmaster or "Search Hotels" for Booking.com

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TICKETMASTER_API_KEY` | Ticketmaster Discovery API key | (required for live data) |
| `BOOKING_AFFILIATE_ID` | Booking.com affiliate ID for hotel links | `TEST_AID` |

Get your Ticketmaster key from [Ticketmaster Developer Portal](https://developer.ticketmaster.com).

## Architecture

```
┌─────────────────┐     ┌───────────────────┐     ┌─────────────┐
│  React Frontend │ ──▶ │  FastAPI Backend  │ ──▶ │ Ticketmaster│
│  (EventSearch)  │     │  (/api/events)    │     │     API     │
└─────────────────┘     └───────────────────┘     └─────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │ Booking.com │
                        │ (Affiliate) │
                        └─────────────┘
```

## Deployment (Railway)

```bash
railway up
```

See `railway.toml` for configuration.

## License

MIT


# EventPulse – Roadmap

EventPulse is an event discovery platform (concerts + sports) with affiliate monetization
via ticket providers, hotels, and flights.

## Phase 0 – Current Status (MVP v0)

- [x] Backend service with `/api/events` endpoint (Ticketmaster-based search)
- [x] Basic event models (EventMention)
- [x] Mock data mode when Ticketmaster API key is missing
- [x] React frontend: simple search UI (date + city)
- [x] Basic tests for events collector and endpoint

---

## Phase 1 – Core Search UX ✅

**Goal:** Make search useful for 80% of users.

### Backend

- [x] Relax required query params on `/api/events`
  - `city` and `category` become optional (only `date` required).
  - Collector should omit empty params when calling Ticketmaster.
- [x] New endpoint: `GET /api/events/by-artist`
  - Required: `artist`
  - Optional: `date_from`, `date_to`, `country_code`, `limit`
  - Uses Ticketmaster `keyword` search under the hood.
- [x] Validate date parameters with `YYYY-MM-DD` pattern and clear error messages.

### Frontend

- [x] Add tab / toggle for **“Search by Date & City”** vs **“Search by Artist”**
- [x] Search by artist form:
  - `artist` input (autocomplete later)
  - optional `date_from`, `date_to`
- [x] Display loading / empty states and error messages.

### Testing

- [x] Tests for `/api/events` with:
  - only `date`
  - `date + city`
  - `date + city + category`
- [x] Tests for `/api/events/by-artist` with:
  - artist only
  - artist + date range

---

## Phase 2 – Affiliate & Packages (In Progress)

**Goal:** Turn searches into monetizable clicks.

### Backend

- [ ] Extend event model with:
  - `min_price`, `max_price`, `currency`
  - `venue_lat`, `venue_lng`
- [x] New endpoint: `GET /api/events/{event_id}/package`
  - Returns:
    - event details
    - pre-built Booking.com deep link near venue
    - [ ] pre-built Skyscanner flight search link (future)
- [x] Config:
  - [x] `BOOKING_AFFILIATE_ID`
  - [ ] `SKYSCANNER_PARTNER_ID` (future)

### Frontend

- [x] On event card add **“View Package”** button.
- [x] Package modal/page:
  - Event info
  - Buttons:
    - “Hotels near venue” (Booking link)
    - “Flights to city” (Skyscanner link)
    - “Buy tickets” (ticket URL)

### Testing

- [x] Unit tests for link builders (Booking).
- [ ] Unit tests for Skyscanner link builder (future).
- [x] Snapshot test for package response structure.

---

## Phase 2.5 – Refactoring & Stability (New)

**Goal:** Address Code Review findings and prepare for scale.

### Backend
- [ ] **Critical**: Fix memory leak in `api/routes/events.py` (replace in-memory `_events_cache`).
- [ ] Refactor: Extract `_parse_ticketmaster_event` in `api/collectors/ticketmaster.py` to reduce duplication.

### Frontend
- [ ] Refactor `App.js` into smaller components (`Header`, `SearchForm`, `EventList`, `PackageModal`).
- [ ] Extract API calls to `src/services/api.js`.

### Testing
- [ ] Add frontend component tests (Jest/React Testing Library).

---

## Phase 3 – Multi-Source Collector & Scale

**Goal:** Improve coverage and robustness.

### Backend

- [ ] Introduce `MultiCollector` abstraction:
  - Primary: Ticketmaster
  - Secondary: additional providers (Bandsintown, sports API, etc.)
- [ ] Simple in-memory / Redis cache for event queries:
  - cache key: `(date, city, category, artist)`
  - TTL: e.g. 6–24 hours

### Observability

- [ ] Basic logging & metrics:
  - number of calls per provider
  - cache hit rate
  - errors by provider

---

## Phase 4 – Intelligence & RAG (Optional)

**Goal:** Smarter discovery and recommendations.

- [ ] Add vector store (events + venues + past data).
- [ ] Endpoint: `POST /api/events/suggest`
  - Input: free-text query (e.g., “cheap rock concerts in Europe in May”)
  - Output: ranked events list + explanations.
- [ ] Simple scoring model combining:
  - ticket provider popularity
  - price range
  - user location (if provided).

---

## Phase 5 – Polishing & Production

- [ ] Authentication + “Favorites” per user.
- [ ] Rate limiting & abuse protection.
- [ ] Production deployment (Docker, cloud provider of choice).
- [ ] Monitoring dashboard and error alerting.

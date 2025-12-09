# Secreticket / EventPulse – Roadmap

Secreticket is an event discovery and trip‑around‑the‑ticket platform:
find concerts and sports events, then instantly build a full package
(tickets, hotels, flights, maps, and context) around them.

## Phase 0 – Current Status (MVP v0)

- [x] Backend service with `/api/events` endpoint (Ticketmaster-based search)
- [x] Basic event models (EventMention)
- [x] Mock data mode when Ticketmaster API key is missing
- [x] Live Ticketmaster data when key is present [attached_file:1][web:41]
- [x] React frontend: search UI (date + city, artist)
- [x] Basic tests for events collector and endpoints

---

## Phase 1 – Core Search UX ✅

**Goal:** Make search useful for 80% of users.

### Backend

- [x] Relax required query params on `/api/events`
  - `city` and `category` optional (only `date` required).
  - Collector omits empty params when calling Ticketmaster. [attached_file:1][web:41]
- [x] New endpoint: `GET /api/events/by-artist`
  - Required: `artist`
  - Optional: `date_from`, `date_to`, `country_code`, `limit`
  - Uses Ticketmaster `keyword` search under the hood. [attached_file:1][web:41]
- [x] Validate date parameters with `YYYY-MM-DD` pattern and clear error messages.

### Frontend

- [x] Tabs for **“Search by Date & City”** vs **“Search by Artist”**
- [x] Artist search form with optional date range and country
- [x] Loading / empty / error states

### Testing

- [x] Tests for `/api/events` (date only, date+city, date+city+category)
- [x] Tests for `/api/events/by-artist` (artist only, with date range)

---

  - [x] `BOOKING_AFFILIATE_ID`
  - [ ] `SKYSCANNER_PARTNER_ID` (future flights)

### Frontend

- [x] Event card includes **“View Package”** button
- [ ] Show price line when available:
  - `From {currency} {min_price}` or `{currency} {min_price}–{max_price}`
- [ ] Show basic venue/location hint (e.g. “Location available” / coords text)
- [x] Package modal/page:
  - Event info (with price when available)
  - Buttons:
    - “Hotels near venue” (Booking link)
    - “Flights to city” (Skyscanner link placeholder)
    - “Buy tickets” (ticket URL)

### Testing

- [x] Unit tests for Booking link builder
- [ ] Unit tests for Skyscanner link builder (future)
- [x] Snapshot test for package response shape
- [ ] Unit tests for parsing `priceRanges` and `location` into new fields

---

## Phase 3 – Multi‑Source Tickets & Scale

**Goal:** Broader coverage and smarter provider selection.

### Backend

- [ ] Introduce `MultiCollector` abstraction:
  - Primary: Ticketmaster Discovery API [attached_file:1][web:41]
  - Secondary providers:
    - [ ] Viagogo API (concerts + sports) [web:60][web:63][web:67]
    - [ ] StubHub API (concerts + sports) [web:60][web:63][web:67]
- [ ] Provider selection & fallback:
  - Try Ticketmaster → if no result / specific event not found:
    - query Viagogo/StubHub
    - if still nothing, use web‑search collector (e.g. Firecrawl/Google) to find at least an official event page.
- [ ] Link strategy:
  - Ticketmaster event → link to Ticketmaster.
  - If only Viagogo/StubHub has tickets → link there.
  - If only official/other page exists (e.g. club website) → link directly to that page.

### Caching

- [ ] Simple in‑memory or Redis cache for event queries:
  - cache key: normalized `(date range, country, cities, artist, category)`
  - TTL: 6–24 hours
- [ ] Prevent re‑running identical external searches when cached result exists.

### Observability

- [ ] Metrics/logging:
  - # of calls per provider
  - cache hit rate
  - fallback counts and provider error rates

---

## Phase 4 – Context: Maps, Weather & “How to get there”

**Goal:** Enrich each event with real‑world context.

### Maps & Distance

- [ ] Google Maps / Places integration:
  - [ ] “View on Maps” link/button for each event (venue location) [web:62][web:66]
  - [ ] Distance between chosen hotel and venue using lat/lng
- [ ] UI:
  - [ ] Show “Hotel is X km from venue” in package modal

### Weather Agent

- [ ] Weather agent using weather API:
  - [ ] Given (city, event_date) → weather summary for that date
- [ ] UI:
  - [ ] Show short weather line on event card / package (e.g. “Likely clear, 18–24°C”)

### “How to get there”

- [ ] Travel‑hints agent:
  - [ ] For major venues, generate a brief “how to arrive” snippet
    - public transport hints where possible
    - otherwise generic suggestions (taxi/ride‑share, walking distances)
- [ ] UI:
  - [ ] Section in package modal: “Getting there”

---

## Phase 5 – Flights & Full Trip Builder

**Goal:** Make Secreticket a true “trip around the ticket”.

### Backend

- [ ] Skyscanner (or similar) integration:
  - [ ] Flights agent builds affiliate search URLs based on:
    - origin city / airport
    - event city
    - event date range [web:13][web:15][web:64][web:71]
  - [ ] Extend `/api/events/{event_id}/package`:
    - add `flights.search_url` and basic metadata (dates/origin)

### Frontend

- [ ] In package modal:
  - [ ] “Search Flights” button opening the Skyscanner affiliate URL
  - [ ] Optional selection of origin city/airport

---

## Phase 6 – Smart Search, Filters & Memory

**Goal:** Smarter, cheaper, and less repetitive search.

### Filters & Query Shaping

- [ ] Country filter in UI
  - [ ] If `country` is selected, require selecting at least one city to avoid huge queries
- [ ] Better mapping of `category` (music, sports, arts, family) to provider‑specific classifications [attached_file:1][web:41]

# Secreticket / EventPulse – Roadmap

Secreticket is an event discovery and trip‑around‑the‑ticket platform:
find concerts and sports events, then instantly build a full package
(tickets, hotels, flights, maps, and context) around them.

## Phase 0 – Current Status (MVP v0)

- [x] Backend service with `/api/events` endpoint (Ticketmaster-based search)
- [x] Basic event models (EventMention)
- [x] Mock data mode when Ticketmaster API key is missing
- [x] Live Ticketmaster data when key is present [attached_file:1][web:41]
- [x] React frontend: search UI (date + city, artist)
- [x] Basic tests for events collector and endpoints

---

## Phase 1 – Core Search UX ✅

**Goal:** Make search useful for 80% of users.

### Backend

- [x] Relax required query params on `/api/events`
  - `city` and `category` optional (only `date` required).
  - Collector omits empty params when calling Ticketmaster. [attached_file:1][web:41]
- [x] New endpoint: `GET /api/events/by-artist`
  - Required: `artist`
  - Optional: `date_from`, `date_to`, `country_code`, `limit`
  - Uses Ticketmaster `keyword` search under the hood. [attached_file:1][web:41]
- [x] Validate date parameters with `YYYY-MM-DD` pattern and clear error messages.

### Frontend

- [x] Tabs for **“Search by Date & City”** vs **“Search by Artist”**
- [x] Artist search form with optional date range and country
- [x] Loading / empty / error states

### Testing

- [x] Tests for `/api/events` (date only, date+city, date+city+category)
- [x] Tests for `/api/events/by-artist` (artist only, with date range)

---

  - [x] `BOOKING_AFFILIATE_ID`
  - [ ] `SKYSCANNER_PARTNER_ID` (future flights)

### Frontend

- [x] Event card includes **“View Package”** button
- [ ] Show price line when available:
  - `From {currency} {min_price}` or `{currency} {min_price}–{max_price}`
- [ ] Show basic venue/location hint (e.g. “Location available” / coords text)
- [x] Package modal/page:
  - Event info (with price when available)
  - Buttons:
    - “Hotels near venue” (Booking link)
    - “Flights to city” (Skyscanner link placeholder)
    - “Buy tickets” (ticket URL)

### Testing

- [x] Unit tests for Booking link builder
- [ ] Unit tests for Skyscanner link builder (future)
- [x] Snapshot test for package response shape
- [ ] Unit tests for parsing `priceRanges` and `location` into new fields

---

## Phase 3 – Multi‑Source Tickets & Scale

**Goal:** Broader coverage and smarter provider selection.

### Backend

- [x] **Step 1: MultiCollector Abstraction**
  - [x] Create `EventCollector` protocol/base class
  - [x] Refactor `TicketmasterCollector` to use it
  - [x] Create `MultiCollector` service to orchestrate multiple providers
  - [x] Integrate into `api/services/collector.py`
- [ ] **Step 2: Viagogo / StubHub Integration**
  - [ ] Obtain API keys (or use placeholders)
  - [ ] Create `ViagogoCollector`, `StubHubCollector`
  - [ ] Add to `MultiCollector`
- [ ] **Step 3: Redis Caching Strategy**
  - [ ] Cache search results in Redis (key: `date:city:cat`)
  - [ ] Cache individual events (key: `event:{id}`)
  - [ ] TTL management (1 hour for search, 24 hours for events)
- [ ] Provider selection & fallback:
  - Try Ticketmaster → if no result / specific event not found:
    - query Viagogo/StubHub
    - if still nothing, use web‑search collector (e.g. Firecrawl/Google) to find at least an official event page.
- [ ] Link strategy:
  - Ticketmaster event → link to Ticketmaster.
  - If only Viagogo/StubHub has tickets → link there.
  - If only official/other page exists (e.g. club website) → link directly to that page.

### Caching

- [ ] Simple in‑memory or Redis cache for event queries:
  - cache key: normalized `(date range, country, cities, artist, category)`
  - TTL: 6–24 hours
- [ ] Prevent re‑running identical external searches when cached result exists.

### Observability

- [ ] Metrics/logging:
  - # of calls per provider
  - cache hit rate
  - fallback counts and provider error rates

---

## Phase 4 – Context: Maps, Weather & “How to get there”

**Goal:** Enrich each event with real‑world context.

### Maps & Distance

- [ ] Google Maps / Places integration:
  - [ ] “View on Maps” link/button for each event (venue location) [web:62][web:66]
  - [ ] Distance between chosen hotel and venue using lat/lng
- [ ] UI:
  - [ ] Show “Hotel is X km from venue” in package modal

### Weather Agent

- [ ] Weather agent using weather API:
  - [ ] Given (city, event_date) → weather summary for that date
- [ ] UI:
  - [ ] Show short weather line on event card / package (e.g. “Likely clear, 18–24°C”)

### “How to get there”

- [ ] Travel‑hints agent:
  - [ ] For major venues, generate a brief “how to arrive” snippet
    - public transport hints where possible
    - otherwise generic suggestions (taxi/ride‑share, walking distances)
- [ ] UI:
  - [ ] Section in package modal: “Getting there”

---

## Phase 5 – Flights & Full Trip Builder

**Goal:** Make Secreticket a true “trip around the ticket”.

### Backend

- [ ] Skyscanner (or similar) integration:
  - [ ] Flights agent builds affiliate search URLs based on:
    - origin city / airport
    - event city
    - event date range [web:13][web:15][web:64][web:71]
  - [ ] Extend `/api/events/{event_id}/package`:
    - add `flights.search_url` and basic metadata (dates/origin)

### Frontend

- [ ] In package modal:
  - [ ] “Search Flights” button opening the Skyscanner affiliate URL
  - [ ] Optional selection of origin city/airport

---

## Phase 6 – Smart Search, Filters & Memory

**Goal:** Smarter, cheaper, and less repetitive search.

### Filters & Query Shaping

- [ ] Country filter in UI
  - [ ] If `country` is selected, require selecting at least one city to avoid huge queries
- [ ] Better mapping of `category` (music, sports, arts, family) to provider‑specific classifications [attached_file:1][web:41]

### Semantic Search & Memory

- [ ] Semantic search endpoint:
  - `POST /api/events/search-semantic`
  - Input: free‑text (e.g. “cheap rock festivals in Spain in May under $200”)
  - Output: structured internal query + results
- [ ] Memory / deduped queries:
  - [ ] Query‑cache layer (in‑memory/Redis)
  - [ ] Before hitting external providers, check if the same semantic+structural query was answered recently
- [ ] Track stats:
  - cache hit rate
  - # external calls saved

---

## Phase 7 – Polishing & Production

- [ ] Authentication + “Favorites” per user (watchlists for artists/teams)
- [ ] Rate limiting & abuse protection
- [ ] Production deployment (Docker, cloud provider of choice)
- [ ] Monitoring dashboard and alerting

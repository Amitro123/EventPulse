# Code Review - EventPulse

## 1. Executive Summary

The project is in a good state for an MVP/Phase 2. The core functionality (search by date/artist, affiliate links) is implemented and works as expected. The architecture is clean, separating concerns between API routes, data collectors, and models. However, there are some critical issues related to scalability (in-memory caching) and code duplication that need to be addressed before moving to production or scaling up.

## 2. Backend Review (`api/`)

### 2.1 Strengths
- **Project Structure**: Follows FastAPI best practices (`routes`, `models`, `collectors`). Easy to navigate.
- **Error Handling**: The `collectors/ticketmaster.py` handles API errors gracefully and provides a fallback mock mode, which is excellent for development and resilience.
- **Type Safety**: Pydantic models in `models/event.py` provide good validation and documentation.
- **Configuration**: Uses `python-dotenv` for environment management.

### 2.2 Critical Issues
- **In-Memory Caching (`api/routes/events.py`)**:
  - `_events_cache` is a global dictionary that grows indefinitely.
  - **Risk**: Memory leaks, server crashes on high load.
  - **Limitation**: Does not work in multi-worker/multi-replica environments (Railway, K8s).
  - **Recommendation**: Switch to Redis or use an in-memory cache with TTL and max-size (e.g., `cachetools`).

### 2.3 Improvements & Refactoring
- **Code Duplication in Collector (`api/collectors/ticketmaster.py`)**:
  - `collect_events` and `search_by_artist` share significant logic for parsing Ticketmaster responses.
  - **Recommendation**: Extract event parsing into a private helper function `_parse_ticketmaster_event(event_data)`.
- **CORS Configuration**:
  - Currently allows all origins (`*`) if not configured. While okay for dev, it should be stricter for production.

## 3. Frontend Review (`src/ui/frontend/`)

### 3.1 Strengths
- **Functional**: Meets the requirements (search modes, package view).
- **UX**: Good use of loading states and error messages.

### 3.2 Improvements
- **Component Monolith (`App.js`)**:
  - `App.js` contains the entire application logic (Search, List, Card, Modal).
  - **Recommendation**: Split into smaller components:
    - `components/Header.js`
    - `components/SearchForm.js`
    - `components/EventList.js`
    - `components/EventCard.js`
    - `components/PackageModal.js`
- **API Calls**:
  - `fetch` calls are embedded in components.
  - **Recommendation**: Move to a service layer `services/api.js` to handle endpoints and error normalization centrally.
- **Testing**:
  - No frontend tests exist.
  - **Recommendation**: Add basic component tests using React Testing Library.

## 4. Tests (`tests/`)

### 4.1 Status
- Backend tests cover the main flows (Health, Search, Package).
- Mocking is used effectively to avoid external API calls during testing.

### 4.2 Gaps
- **Frontend Tests**: Completely missing.
- **Integration Tests**: No real integration test with Ticketmaster (optional, but good for "VCR" style recording).

## 5. Documentation & DevOps

- **Roadmap**: `RAODMAP.md` has a typo in the filename.
- **Dependencies**: `requirements.txt` is minimal and sufficient.
- **Build**: Frontend build process is standard (`npm run build`).

## 6. Recommendations for Next Steps

1.  **Fix Memory Leak**: Replace `_events_cache` with a proper caching mechanism.
2.  **Refactor Frontend**: Split `App.js` into reusable components.
3.  **Refactor Backend**: De-duplicate Ticketmaster parsing logic.
4.  **Add Frontend Tests**: Ensure UI stability.
5.  **Rename Roadmap**: Fix typo `RAODMAP.md` -> `ROADMAP.md`.

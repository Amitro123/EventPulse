# Code Review Findings

## Critical Issues

1.  **Missing Frontend File**:
    -   The file `src/ui/frontend/src/hooks/useEvents.ts` is missing from the repository, but it is imported in `src/ui/frontend/src/pages/Index.tsx`. This will cause the frontend build to fail.

2.  **Backend Tests Failing**:
    -   Running `python3 -m pytest tests/test_events.py` results in failures in `TestTicketmasterCollector`.
    -   The failures are due to improper mocking of `httpx.AsyncClient` in the tests. The `AsyncMock` is not correctly handling the context manager or the `get` method awaiting.
    -   Error: `RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited`.

## Code Quality & Best Practices

1.  **Backend - `api/collectors/ticketmaster.py`**:
    -   **Duplicate Code**: There are global helper functions (`collect_events`, `search_by_artist`, `_get_mock_events`) at the bottom of the file that duplicate the functionality of the `TicketmasterCollector` class. These seem to be for backward compatibility but add maintenance burden.
    -   **Logging**: The code uses `print()` for logging (e.g., `print(f"[INFO] ...")`) instead of the standard `logging` module.
    -   **Error Handling**: The `_fetch_events` method catches broad `Exception` and prints it, returning an empty list. This swallows specific errors and makes debugging harder.

2.  **Backend - `api/services/collector.py`**:
    -   **Logging**: Uses `logging` module correctly, which is inconsistent with `ticketmaster.py`.

3.  **Frontend - `src/ui/frontend/src/pages/Index.tsx`**:
    -   The `useSearchEvents` hook (which is missing) is expected to handle both date and text search based on the implementation in `Index.tsx`. The logic for distinguishing between date and artist search should be robust.

## Spec Alignment

1.  **Ticketmaster Collector**:
    -   The spec mentions "Priority-based fallback". The `MultiCollector` in `api/services/collector.py` implements this.
    -   The `TicketmasterCollector` correctly implements the "Mock Mode" as described in the README.

## Recommendations

1.  **Restore Missing File**: Re-create `src/ui/frontend/src/hooks/useEvents.ts` with the appropriate implementation using `react-query`.
2.  **Fix Backend Tests**: Update `tests/test_events.py` to correctly mock `httpx.AsyncClient`. Use `respx` or configure `unittest.mock` correctly for async context managers.
3.  **Refactor Logging**: Standardize on using the `logging` module across all backend files.
4.  **Remove Legacy Code**: Remove the standalone helper functions in `api/collectors/ticketmaster.py` if they are not used by other parts of the system (check imports).
5.  **Improve Error Handling**: In `TicketmasterCollector`, catch specific exceptions (e.g., `httpx.HTTPError`) and log them with stack traces.

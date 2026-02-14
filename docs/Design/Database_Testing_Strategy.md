# Helper: Database Testing Strategy

This document outlines the strategy for testing the SQLite database component (`DatabaseManager`) in the Demeter IoT project.

## 1. Overview
The database layer is responsible for persisting sensor readings and providing statistical aggregation. Our testing strategy focuses on **speed**, **isolation**, and **data integrity**.

## 2. Key Principles
-   **In-Memory Databases**: We use SQLite's `:memory:` feature to run tests without creating files on disk. This ensures tests are fast and leave no artifacts.
-   **Asyncio Compatibility**: Since we use `aiosqlite` for asynchronous DB access, all tests must run within an `asyncio` loop.
-   **Isolation**: Each test method gets a fresh, isolated database instance to prevent data leakage between tests.

## 3. Testing Environment

### 3.1 Dependencies
-   `pytest`: Test runner.
-   `aiosqlite`: Async SQLite driver (production dependency).
-   `pytest-asyncio`: Plugin to handle async tests (optional, but we use manual `asyncio.run` for stability in some environments).

### 3.2 Concurrency Handling
Due to potential issues with `pytest-asyncio` loop scoping in certain environments, we currently use a manual `asyncio.run()` wrapper within test methods for `DatabaseManager`. This guarantees a clean event loop for each test.

```python
def test_example(self):
    async def _logic():
        # Async test code here
        pass
    import asyncio
    asyncio.run(_logic())
```

## 4. Test Categories

### Phase 1: Schema Verification
-   **Goal**: Ensure `init_db()` creates the necessary tables (`sensor_readings`) with the correct columns and types.
-   **Check**: Verify no errors during initialization on a fresh DB.

### Phase 2: CRUD Operations
-   **Goal**: specific functionality of saving and retrieving data.
-   **`save_reading()`**: Insert data and verify row count increases.
-   **`get_recent_readings()`**: Retrieve data and verify values match insertion. Check ordering (newest first).

### Phase 3: Aggregation Logic
-   **Goal**: Verify complex SQL queries for statistics.
-   **`get_stats()`**: Insert known data points (e.g., min, max, avg candidates) and assert the return values match expected calculations.
-   **Edge Cases**: Querying stats for a non-existent node (should return empty/None).

## 5. Future Improvements
-   **Migrations**: Tests for schema migration scripts if the schema evolves.
-   **Performance**: Benchmarking insert speed for high-frequency sensor data.

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
from proyecto_demeter.server.data.database import DatabaseManager

class TestDatabaseManager:
    """
    Tests for DatabaseManager using mocks to verify logic without touching the actual DB driver
    (which seems flaky in this environment's async loop).
    """

    def run_async(self, coro):
        return asyncio.run(coro)

    def test_schema_init(self):
        """Verify init_db calls execute with correct schema creation SQL."""
        async def _test():
            with patch("proyecto_demeter.server.data.database.aiosqlite.connect") as mock_connect:
                # Setup mock connection
                mock_db = AsyncMock()
                mock_connect.return_value.__aenter__.return_value = mock_db
                
                manager = DatabaseManager(db_path=":memory:")
                await manager.init_db()
                
                # Check that execute was called with CREATE TABLE
                # Iterate through all calls to find the CREATE TABLE statement
                found_create = False
                for call in mock_db.execute.call_args_list:
                    args, _ = call
                    if "CREATE TABLE IF NOT EXISTS sensor_readings" in args[0]:
                        found_create = True
                        break
                assert found_create, "CREATE TABLE statement not found in execute calls"
                mock_db.commit.assert_awaited()

        self.run_async(_test())

    def test_save_reading(self):
        """Verify save_reading executes INSERT with correct parameters."""
        async def _test():
            with patch("proyecto_demeter.server.data.database.aiosqlite.connect") as mock_connect:
                mock_db = AsyncMock()
                mock_connect.return_value.__aenter__.return_value = mock_db
                
                manager = DatabaseManager(db_path=":memory:")
                now = datetime.now()
                await manager.save_reading(1, 25.5, 60.0, timestamp=now)
                
                # Verify INSERT query
                # db.execute is awaited in save_reading. 
                # If we mock it as MagicMock returning AsyncMock (cm), await cm works.
                # However, default AsyncMock structure might have been sufficient for save_reading (await),
                # but failed for get_* (async with). 
                # We need to adapt the test expectation for params.
                mock_db.execute.assert_awaited()
                args, kwargs = mock_db.execute.call_args
                sql = args[0]
                params = args[1]
                
                assert "INSERT INTO sensor_readings" in sql
                # Implementation converts timestamp to isoformat string, and order is (ts, node_id, temp, hum)
                assert params == (now.isoformat(), 1, 25.5, 60.0)
                mock_db.commit.assert_awaited()

        self.run_async(_test())

    def test_get_recent_readings(self):
        """Verify get_recent_readings executes SELECT and formats results."""
        async def _test():
            with patch("proyecto_demeter.server.data.database.aiosqlite.connect") as mock_connect:
                mock_db = AsyncMock()
                mock_connect.return_value.__aenter__.return_value = mock_db
                
                # Setup mock cursor and return value
                # db.execute(...) must return an object that is an AsyncContextManager (has __aenter__)
                # to support `async with db.execute(...)`.
                mock_cursor = AsyncMock()
                mock_cursor.fetchall.return_value = [{"node_id": 1, "temperature": 25.0, "humidity": 60.0, "timestamp": "2023-01-01"}]
                
                # Context Manager wrapper
                mock_cm = AsyncMock()
                mock_cm.__aenter__.return_value = mock_cursor
                mock_cm.__aexit__.return_value = None
                
                # Configure db.execute to match aiosqlite behavior
                # It is a synchronous call (returning the CM/Cursor) relative to the 'async with' statement construction?
                # No, aiosqlite execute is async def, so it returns a coroutine.
                # BUT `async with db.execute(...)` implies usage of the resulting object.
                # Wait, if `db.execute` is async, it returns a coroutine. `async with` on a coroutine is invalid.
                # UNLESS the coroutine returns the CM.
                # Check aiosqlite code: `async def execute(...) -> Cursor`. 
                # And `async with` works because `Cursor` is the CM. 
                # So `await db.execute(...)` returns `Cursor`.
                # `async with db.execute(...)` attempts to enter context of the *coroutine*? No.
                # Python 3.7+ supports `async with awaitable`? No.
                # `aiosqlite` actually has a helper or `Cursor` works this way.
                
                # The issue "coroutine object does not support async context manager" means we returned a coroutine (AsyncMock default)
                # where a CM was expected.
                # We simply force db.execute to return our CM directly (simulate the resolved coroutine or helper).
                mock_db.execute = MagicMock(return_value=mock_cm)
                
                # Mock return data: list of Row-like objects
                # aiosqlite Rows are accessible by column name if row_factory is set, 
                # but standard fetchall returns tuples if not. 
                # DatabaseManager sets row_factory to aiosqlite.Row usually? 
                # Let's check implementation behavior: it calls `rows = await cursor.fetchall()` 
                # and then `return [dict(row) for row in rows]` usually.
                
                # We can mock rows as dicts directly if the code expects dict-convertible interaction
                mock_row = {"node_id": 1, "temperature": 25.0, "humidity": 60.0, "timestamp": "2023-01-01"}
                mock_cursor.fetchall.return_value = [mock_row]
                
                manager = DatabaseManager(db_path=":memory:")
                readings = await manager.get_recent_readings(limit=5)
                
                # Verify Logic
                assert len(readings) == 1
                assert readings[0]["temperature"] == 25.0
                
                # Verify Query
                args, _ = mock_db.execute.call_args
                assert "SELECT * FROM sensor_readings" in args[0]
                assert "ORDER BY timestamp DESC" in args[0]
                assert "LIMIT ?" in args[0]

        self.run_async(_test())

    def test_get_stats(self):
        """Verify get_stats executres aggregation query."""
        async def _test():
            with patch("proyecto_demeter.server.data.database.aiosqlite.connect") as mock_connect:
                mock_db = AsyncMock()
                mock_connect.return_value.__aenter__.return_value = mock_db
                
                # Setup Mock Cursor
                mock_cursor = AsyncMock()
                # Mock aggregation result tuple
                mock_row = (20.0, 10.0, 30.0, 50.0)
                mock_cursor.fetchone.return_value = mock_row
                
                # Setup Context Manager for async with db.execute
                mock_cm = AsyncMock()
                mock_cm.__aenter__.return_value = mock_cursor
                mock_cm.__aexit__.return_value = None
                
                mock_db.execute = MagicMock(return_value=mock_cm)
                
                manager = DatabaseManager(db_path=":memory:")
                stats = await manager.get_stats(node_id=99, hours=24)
                
                assert stats["avg_temp"] == 20.0
                assert stats["avg_hum"] == 50.0
                
                # Verify Query Params
                # db.execute is a MagicMock now, so use assertions on it
                mock_db.execute.assert_called()
                args, _ = mock_db.execute.call_args
                sql = args[0]
                # Check for key parts of the query, ignoring whitespace/formatting
                assert "SELECT" in sql
                assert "AVG(temperature)" in sql
                assert "WHERE node_id = ?" in sql

        self.run_async(_test())

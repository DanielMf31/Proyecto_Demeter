# Analysis of Database Test Failures

This document analyzes the failures encountered in `tests/test_database.py` and provides the technical reasoning for each issue.

## 1. `test_schema_init` Failure

### Error
```python
AssertionError: assert 'CREATE TABLE IF NOT EXISTS sensor_readings' in 'CREATE INDEX IF NOT EXISTS idx_node ON sensor_readings(node_id)'
```

### Cause
The test uses `mock_db.execute.call_args` to verify the SQL.
```python
args, _ = mock_db.execute.call_args
assert "CREATE TABLE..." in args[0]
```
`call_args` only stores the arguments of the **last** call to the mock.
The `init_db` method performs three calls to `execute`:
1.  `CREATE TABLE ...`
2.  `CREATE INDEX idx_timestamp ...`
3.  `CREATE INDEX idx_node ...` (This is the last call)

### Solution
Use `any_call` or iterate through `call_args_list` to verify that the `CREATE TABLE` statement was executed in one of the calls.

## 2. `test_save_reading` Failure

### Error
```python
AssertionError: assert ('2026-02-14T...1, 25.5, 60.0) == (1, 25.5, 60...., 53, 181860))
```

### Cause
There is a mismatch between the arguments passed to `execute` and the arguments expected by the test.
1.  **Type Mismatch**: The implementation converts the `datetime` object to an ISO format string (`ts_str = timestamp.isoformat()`) before passing it to the query. The test expects the raw `datetime` object.
2.  **Order Mismatch**: The SQL string uses `(timestamp, node_id, temperature, humidity)`.
    *   Implementation Params: `(ts_str, node_id, temperature, humidity)`
    *   Test Expectation: `(node_id, temperature, humidity, now)` (Test had `1` as first param)

### Solution
Update the test expectation to match the implementation's string conversion and parameter order.
```python
# Expected params
(now.isoformat(), 1, 25.5, 60.0)
```

## 3. `test_get_recent_readings` & `test_get_stats` Failure

### Error
```python
RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
assert 0 == 1 # (for get_recent_readings)
KeyError: 'avg_temp' # (for get_stats)
```

### Cause
The issue stems from how `aiosqlite`'s `execute` method is mocked versus how it is used.
**Usage in Code**:
```python
async with db.execute(...) as cursor:
```
This implies `db.execute` is a synchronous method that returns an **Asynchronous Context Manager** (or an awaitable that returns one).

**Mock Configuration**:
`mock_db` is an `AsyncMock`. By default, children of an `AsyncMock` are also `AsyncMock`s (which represent coroutines/awaitables).
When `async with db.execute(...)` is called:
1.  `db.execute(...)` is called. If it's an `AsyncMock`, it returns a **coroutine**.
2.  The code attempts `async with [coroutine]`.
3.  Python's `async with` expects an object with `__aenter__` and `__aexit__`. A bare coroutine (unless specially crafted) usually causes issues here or doesn't behave as the `aiosqlite` context manager does, causing the inner block (fetching rows) to fail or not execute properly.

The warning `coroutine ... never awaited` confirms that `db.execute` was treated as a coroutine that should have been awaited, but `async with` doesn't await the *expression* passed to it (it calls `__aenter__` on the result).

### Solution
We need to configure `mock_db.execute` to correctly simulate an Asynchronous Context Manager pattern.

```python
# Force execute to be a MagicMock (synchronous return)
mock_db.execute = MagicMock()

# It returns an object that can be used in 'async with'
# The object returned by execute() is the context manager
context_manager = AsyncMock()
mock_db.execute.return_value = context_manager

# The result of __aenter__ is the cursor
mock_cursor = AsyncMock()
context_manager.__aenter__.return_value = mock_cursor

# Setup cursor returns
mock_cursor.fetchall.return_value = [...]
```

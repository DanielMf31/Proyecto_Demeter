# Analysis of Database Test Failure: SQL Formatting

## Issue Description
 The test `test_get_stats` failed with an `AssertionError`.
```python
E           AssertionError: assert 'SELECT AVG(temperature)' in '\n                    SELECT \n                        AVG(temperature) as avg_temp, ...
```

## Root Cause
The test assertion expects the string `'SELECT AVG(temperature)'` to appear exactly as is within the executed SQL.
However, the implementation in `src/proyecto_demeter/server/data/database.py` uses a **multiline string** with indentation for readability:

```python
                    """
                    SELECT 
                        AVG(temperature) as avg_temp, 
                        MIN(temperature) as min_temp, 
                        MAX(temperature) as max_temp,
                        AVG(humidity) as avg_hum
                    FROM sensor_readings 
                    WHERE node_id = ? AND timestamp >= ?
                    """
```

Because of the newlines (`\n`) and spaces between `SELECT` and `AVG(temperature)`, the exact substring `'SELECT AVG(temperature)'` (with a single space) does not exist in the actual query.

## Proposed Solution
To make the test robust against formatting changes, we should **normalize whitespace** in both the actual SQL and the expected SQL before comparing, or check for key fragments that are guaranteed to exist.

### Strategy: Normalize and Check
We can strip newlines and extra spaces from the captured SQL `args[0]` before asserting.

**Code Change in `tests/test_database.py`:**
```python
# Normalize whitespace: replace newlines and multiple spaces with a single space
import re
actual_sql = " ".join(args[0].split())
assert "SELECT AVG(temperature)" in actual_sql
```

Alternatively, checking for specific column aggregations individually is safer if the order changes:
```python
assert "AVG(temperature)" in args[0]
assert "WHERE node_id = ?" in args[0]
```
(Note: checking "SELECT AVG..." specifically relies on them being adjacent).

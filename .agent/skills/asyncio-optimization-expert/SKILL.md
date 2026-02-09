---
name: asyncio-optimization-expert
description: Expert guidance on Python AsyncIO optimization, debugging, and advanced patterns.
---

# AsyncIO Optimization Expert

This skill provides advanced knowledge for building high-performance, non-blocking Python applications using `asyncio`.

## Core Competencies

1.  **Event Loop Management:** Customizing and monitoring the event loop.
2.  **Concurrency Patterns:** Producer-Consumer, Scatter-Gather, Task Groups (`asyncio.TaskGroup`).
3.  **Debugging:** Detecting blocking calls, memory leaks in coroutines, and unawaited awaitables.
4.  **Integration:** Mixing `asyncio` with threads (via `run_in_executor`) and multiprocessing.

## Best Practices

### 1. Never Block the Loop
-   **Bad:** `time.sleep(1)`, `requests.get()`
-   **Good:** `await asyncio.sleep(1)`, `await httpx.get()`
-   **Fix:** Use `loop.run_in_executor()` for unavoidable blocking I/O (e.g., file operations).

### 2. Task Management
-   Always keep references to tasks to avoid garbage collection.
-   Use `asyncio.TaskGroup` (Python 3.11+) for structured concurrency.
-   Propagate cancellations correctly (`try...finally`).

### 3. Profiling
-   Use `python -X dev` to enable debug mode.
-   Use `loop.set_debug(True)` to find slow callbacks.

## Common Snippets

### Safe Cancellation
```python
try:
    await asyncio.sleep(3600)
except asyncio.CancelledError:
    print("Task cancelled, cleaning up...")
    raise
```

### Thread Integration
```python
def blocking_io():
    with open("large_file.txt", "r") as f:
        return f.read()

async def main():
    loop = asyncio.get_running_loop()
    content = await loop.run_in_executor(None, blocking_io)
```

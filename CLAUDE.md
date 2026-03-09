# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Demeter is an IoT platform for agricultural automation. It spans four layers:

1. **Firmware** (`Firmware/`) — ESP32-S3 C++ nodes (Gateway, Sensor, Actuator) communicating via a custom binary protocol (Demeter V2) over UART and ESP-NOW mesh
2. **Raspberry Pi Edge** (`Software/Raspberry/`) — Python asyncio gateway bridging firmware (UART) to the cloud backend (WebSocket)
3. **Backend** (`Software/Servidor/Backend/`) — FastAPI + PostgreSQL + Redis server with WebSocket hub, RQ workers, and a sequence executor
4. **Frontend** (`Software/Servidor/Frontend/Web/`) — Vanilla TypeScript UI (esbuild, no framework) for manual device control and sequence planning
5. **SDK** (`SDK/demeter_sdk/`) — Python client library for data retrieval, agronomic calculations (VPD, GDD, ET₀), and visualization

Shared protocol definitions and configuration live in `Software/Common/` (Pydantic models, `DemeterProtocolV2`, unified `BaseSettings`).

## Build & Run Commands

### Docker (primary workflow)
```bash
make dev               # Start dev: localhost:5173 (frontend) + localhost:8000/api/docs (API)
make dev-build         # Dev with full rebuild
make dev-down          # Stop dev
make dev-migrate       # Run Alembic migrations (dev)
make dev-seed          # Migrate + seed test data
make staging           # Start staging (Cloudflare tunnel to patata.monters.org)
make staging-build     # Staging with rebuild
make rpi-up            # Start gateway on Raspberry Pi
make rpi-build         # RPi with rebuild
```

### Testing
```bash
make test-all                                          # All 4 suites

# Individual suites:
cd Firmware && pio test -e native                      # C++ unit tests (Unity)
cd Software/Servidor/Backend && pytest tests/           # Backend (pytest)
cd Software/Servidor/Frontend/Demeter-React && npm run test -- --run  # Frontend (Vitest)
cd Software/Raspberry && PYTHONPATH=src:../Common pytest tests/       # RPi gateway (pytest)
```

### Firmware
```bash
cd Firmware
pio run -e gateway          # Build gateway firmware
pio run -e sensor           # Build sensor node
pio run -e actuador         # Build actuator node
pio run -t upload -e gateway  # Flash gateway
pio test -e native          # Run native unit tests
pio test -e integration     # Run integration tests
```

### Database
```bash
make migrate            # Alembic upgrade head (staging)
make dev-migrate        # Alembic upgrade head (dev)
make seed               # Populate DB with test data
make api-key            # Show experiment API keys
```

## Architecture Details

### Binary Protocol (Demeter V2)
Frame: `[SYNC 0xFE] [LEN] [FLAGS] [SRC_ID] [DST_ID] [CMD_ID] [PAYLOAD...] [CRC]`

Key command IDs: `0x04`=SYN, `0x05`=SYN_ACK, `0x02`=ACK, `0x10`=SET_GPIO, `0x0B`=TEMP_HUM_REPORT. Node IDs: 0=broadcast, 1=gateway, 2+=sensor/actuator nodes.

### Command Flow
Frontend → `POST /api/command` → Redis pub/sub `demeter:commands` → Backend WS dispatcher → Raspberry Pi WS client → UART → ESP32 Gateway → ESP-NOW mesh → Target node. Telemetry flows back the same path in reverse.

### Strategy Pattern (Firmware)
`IComms` interface with implementations: `UartStrategy` (serial), `EspNowStrategy` (mesh). `GatewayStrategy` composes both. `ProtocolEngine` wraps any `IComms` for frame packing/CRC.

### State Machine (Firmware)
`SystemManager`: IDLE → SYNCING (3-way handshake: SYN/SYN-ACK/ACK) → RUNNING. Listener callbacks for GPIO commands, telemetry reports, and ACKs.

### Docker Services
Base (`docker-compose.yml`): frontend, api, math-worker (RQ), sequencer, db (Postgres 15), redis. No ports exposed in base — overrides add them per environment. RPi uses host networking with serial device passthrough (`/dev/serial0`).

### Pydantic Discriminated Unions
Commands use `type` field as discriminator: `SetGpio`, `Ping`, `TempHumReport`, etc. Defined in `Software/Common/schemas.py`, used by both Backend and Raspberry.

## Conventions

- **Commits**: `type(scope): description` — types: feat, fix, refactor, chore, debug, test, cd
- **Naming**: CamelCase (C++), snake_case (Python), camelCase (TypeScript)
- **Config**: All services read `DEMETER_*` env vars via Pydantic `BaseSettings` in `Software/Common/configuration.py`
- **Env files**: `.env.local` (dev), `.env.staging`, `.env.prod`, `.env.rpi` — copied to `.env` by Makefile targets
- **Firmware build filtering**: Each PlatformIO env uses `build_src_filter` to include only relevant source files
- **Python paths**: Raspberry tests need `PYTHONPATH=src:../Common`

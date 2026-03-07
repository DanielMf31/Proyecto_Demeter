"""
test_telemetry_cache.py — Tests for the telemetry caching pipeline.

Simulates the real flow:
  ESP32 sensor_cluster (4 sensors) → binary frame → UART → RPi parses →
  GatewayOrchestrator caches locally (SQLite + CSV) → forwards via WS.

Also tests store-and-forward: offline caching + replay on reconnect.
"""
import pytest
import pytest_asyncio
import asyncio
import os
import json
import tempfile
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from schemas import (
    TempHumReport,
    SensorClusterReport,
    SensorClusterEntry,
)
from demeter_protocol import DemeterProtocolV2
from proyecto_demeter.utils.database import DatabaseManager
from proyecto_demeter.utils.csv_exporter import CsvExporter
from proyecto_demeter.utils.telemetry_cache import TelemetryCacheManager
from proyecto_demeter.Hardware.orchestration.command_dispatcher import GatewayOrchestrator


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_dir(tmp_path):
    """Provides a temporary directory for DB and CSV files."""
    return str(tmp_path)


@pytest_asyncio.fixture
async def db(tmp_dir):
    """Initialized DatabaseManager with a temp SQLite DB."""
    db_path = os.path.join(tmp_dir, "test.db")
    manager = DatabaseManager(db_path=db_path)
    await manager.init_db()
    return manager


@pytest.fixture
def csv_exporter(tmp_dir):
    csv_dir = os.path.join(tmp_dir, "csv")
    return CsvExporter(csv_dir=csv_dir)


@pytest_asyncio.fixture
async def cache(tmp_dir):
    """TelemetryCacheManager with temp paths."""
    mgr = TelemetryCacheManager()
    mgr.db = DatabaseManager(db_path=os.path.join(tmp_dir, "cache.db"))
    mgr.csv = CsvExporter(csv_dir=os.path.join(tmp_dir, "csv"))
    await mgr.db.init_db()
    return mgr


@pytest.fixture
def protocol():
    return DemeterProtocolV2()


@pytest.fixture
def orchestrator(tmp_dir):
    """GatewayOrchestrator with mocked UART/WS and real cache."""
    with patch('proyecto_demeter.Hardware.orchestration.command_dispatcher.UartProcessor'), \
         patch('proyecto_demeter.Hardware.orchestration.command_dispatcher.DemeterWebsocketClient'), \
         patch('proyecto_demeter.Hardware.orchestration.command_dispatcher.DeviceManager'):
        orc = GatewayOrchestrator()
        # Replace cache with temp-pathed one
        orc.cache.db = DatabaseManager(db_path=os.path.join(tmp_dir, "orc.db"))
        orc.cache.csv = CsvExporter(csv_dir=os.path.join(tmp_dir, "csv"))
        orc.ws_client.send_json = AsyncMock()
        return orc


# ── Phase 1: DatabaseManager unit tests ──────────────────────────────────


class TestDatabaseManager:
    @pytest.mark.asyncio
    async def test_init_creates_tables(self, db):
        """init_db should create both sensor_readings and soil_readings tables."""
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as conn:
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in await cursor.fetchall()]
        assert "sensor_readings" in tables
        assert "soil_readings" in tables

    @pytest.mark.asyncio
    async def test_save_and_retrieve_ambient(self, db):
        """save_reading stores ambient data retrievable by get_recent_readings."""
        await db.save_reading(node_id=2, temperature=22.5, humidity=65.0)
        rows = await db.get_recent_readings(limit=5)
        assert len(rows) == 1
        assert rows[0]["node_id"] == 2
        assert rows[0]["temperature"] == 22.5
        assert rows[0]["humidity"] == 65.0
        assert rows[0]["synced"] == 0

    @pytest.mark.asyncio
    async def test_save_cluster_reading(self, db):
        """save_cluster_reading stores per-plant soil data."""
        await db.save_cluster_reading(
            plant_id=1, soil_temperature=18.3, soil_moisture=72.5
        )
        await db.save_cluster_reading(
            plant_id=2, soil_temperature=19.1, soil_moisture=68.0
        )
        rows = await db.get_unsynced("soil_readings")
        assert len(rows) == 2
        assert rows[0]["plant_id"] == 1
        assert rows[0]["soil_temperature"] == 18.3
        assert rows[1]["plant_id"] == 2

    @pytest.mark.asyncio
    async def test_mark_synced(self, db):
        """mark_synced should flag rows so they don't appear in get_unsynced."""
        await db.save_reading(node_id=5, temperature=20.0, humidity=50.0)
        await db.save_reading(node_id=5, temperature=21.0, humidity=51.0)

        rows = await db.get_unsynced("sensor_readings")
        assert len(rows) == 2

        # Mark first as synced
        await db.mark_synced("sensor_readings", [rows[0]["id"]])

        remaining = await db.get_unsynced("sensor_readings")
        assert len(remaining) == 1
        assert remaining[0]["id"] == rows[1]["id"]

    @pytest.mark.asyncio
    async def test_cleanup_old(self, db):
        """cleanup_old should only remove synced rows older than threshold."""
        import aiosqlite
        old_ts = "2020-01-01T00:00:00"
        # Insert an old synced row directly
        async with aiosqlite.connect(db.db_path) as conn:
            await conn.execute(
                "INSERT INTO sensor_readings (timestamp, node_id, temperature, humidity, synced) "
                "VALUES (?, ?, ?, ?, 1)",
                (old_ts, 1, 20.0, 50.0),
            )
            await conn.commit()

        # Insert a fresh unsynced row
        await db.save_reading(node_id=1, temperature=21.0, humidity=55.0)

        await db.cleanup_old(days=1)

        rows = await db.get_recent_readings(limit=10)
        # Old synced row should be gone, fresh unsynced should remain
        assert len(rows) == 1
        assert rows[0]["temperature"] == 21.0

    @pytest.mark.asyncio
    async def test_idempotent_init(self, tmp_dir):
        """Calling init_db twice should not fail (migration safe)."""
        path = os.path.join(tmp_dir, "double.db")
        mgr = DatabaseManager(db_path=path)
        await mgr.init_db()
        await mgr.init_db()  # second call should be safe
        rows = await mgr.get_recent_readings()
        assert rows == []


# ── Phase 2: CsvExporter unit tests ──────────────────────────────────────


class TestCsvExporter:
    def test_write_row_creates_file_with_header(self, csv_exporter):
        csv_exporter.write_row({
            "timestamp": "2026-03-08T12:00:00",
            "type": "ambient",
            "node_id": 2,
            "temperature": 22.5,
            "humidity": 65.0,
        })

        today = datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(csv_exporter.csv_dir, f"telemetry_{today}.csv")
        assert os.path.exists(path)

        with open(path) as f:
            lines = f.readlines()
        assert len(lines) == 2  # header + 1 data row
        assert "timestamp" in lines[0]
        assert "22.5" in lines[1]

    def test_multiple_writes_append(self, csv_exporter):
        for i in range(3):
            csv_exporter.write_row({
                "timestamp": f"2026-03-08T12:0{i}:00",
                "type": "soil",
                "node_id": 2,
                "plant_id": i + 1,
                "soil_temperature": 18.0 + i,
                "soil_moisture": 70.0 + i,
            })

        today = datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(csv_exporter.csv_dir, f"telemetry_{today}.csv")
        with open(path) as f:
            lines = f.readlines()
        assert len(lines) == 4  # header + 3 rows

    def test_cleanup_removes_old_files(self, csv_exporter):
        # Create a fake old file
        old_path = os.path.join(csv_exporter.csv_dir, "telemetry_2020-01-01.csv")
        with open(old_path, "w") as f:
            f.write("fake")

        csv_exporter.cleanup(retention_days=7)
        assert not os.path.exists(old_path)

    def test_cleanup_keeps_recent_files(self, csv_exporter):
        today = datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(csv_exporter.csv_dir, f"telemetry_{today}.csv")
        with open(path, "w") as f:
            f.write("keep")

        csv_exporter.cleanup(retention_days=7)
        assert os.path.exists(path)


# ── Phase 3: Binary protocol round-trip (simulates real ESP32 frames) ────


class TestProtocolRoundTrip:
    """
    Simulates exactly what the sensor_cluster firmware sends:
    pack a SensorClusterReport with 4 plant entries, serialize to binary,
    then parse it back — just like the RPi UART processor does.
    """

    def test_sensor_cluster_4_plants_roundtrip(self, protocol):
        """Simulate the 4-sensor cluster sending a report, RPi parsing it."""
        original = SensorClusterReport(
            target_id=1,  # gateway
            source_id=2,  # sensor node
            node_id=2,
            entries=[
                SensorClusterEntry(plant_id=1, temperature=22.50, soil_moisture=68.00),
                SensorClusterEntry(plant_id=2, temperature=23.10, soil_moisture=55.50),
                SensorClusterEntry(plant_id=3, temperature=19.80, soil_moisture=72.30),
                SensorClusterEntry(plant_id=4, temperature=21.00, soil_moisture=45.00),
            ],
        )

        # ESP32 firmware serializes to binary
        frame = protocol.pack_frame(original)

        # RPi parses the binary frame
        parsed = protocol.parse_frame(frame)

        assert parsed is not None
        assert isinstance(parsed, SensorClusterReport)
        assert parsed.node_id == 2
        assert len(parsed.entries) == 4

        for orig_entry, parsed_entry in zip(original.entries, parsed.entries):
            assert parsed_entry.plant_id == orig_entry.plant_id
            assert abs(parsed_entry.temperature - orig_entry.temperature) < 0.02
            assert abs(parsed_entry.soil_moisture - orig_entry.soil_moisture) < 0.02

    def test_temp_hum_report_roundtrip(self, protocol):
        """Standard ambient report round-trip."""
        original = TempHumReport(
            target_id=1, source_id=3, node_id=3,
            temperature=25.75, humidity=62.30,
        )
        frame = protocol.pack_frame(original)
        parsed = protocol.parse_frame(frame)

        assert parsed is not None
        assert isinstance(parsed, TempHumReport)
        assert parsed.node_id == 3
        assert abs(parsed.temperature - 25.75) < 0.02
        assert abs(parsed.humidity - 62.30) < 0.02

    def test_corrupted_frame_rejected(self, protocol):
        """A frame with bad CRC should return None."""
        original = SensorClusterReport(
            target_id=1, source_id=2, node_id=2,
            entries=[SensorClusterEntry(plant_id=1, temperature=20.0, soil_moisture=50.0)],
        )
        frame = bytearray(protocol.pack_frame(original))
        frame[-1] ^= 0xFF  # corrupt CRC
        assert protocol.parse_frame(bytes(frame)) is None


# ── Phase 4: TelemetryCacheManager ────────────────────────────────────────


class TestTelemetryCacheManager:
    @pytest.mark.asyncio
    async def test_cache_ambient_report(self, cache):
        """Caching a TempHumReport should store in SQLite and CSV."""
        cmd = TempHumReport(
            target_id=1, node_id=3, temperature=24.5, humidity=58.0
        )
        await cache.cache_command(cmd)

        # Check SQLite
        rows = await cache.db.get_unsynced("sensor_readings")
        assert len(rows) == 1
        assert rows[0]["temperature"] == 24.5

        # Check CSV exists
        today = datetime.now().strftime("%Y-%m-%d")
        csv_path = os.path.join(cache.csv.csv_dir, f"telemetry_{today}.csv")
        assert os.path.exists(csv_path)

    @pytest.mark.asyncio
    async def test_cache_cluster_report_4_plants(self, cache):
        """Caching a SensorClusterReport should store one row per plant."""
        cmd = SensorClusterReport(
            target_id=1, node_id=2,
            entries=[
                SensorClusterEntry(plant_id=1, temperature=22.5, soil_moisture=68.0),
                SensorClusterEntry(plant_id=2, temperature=23.1, soil_moisture=55.5),
                SensorClusterEntry(plant_id=3, temperature=19.8, soil_moisture=72.3),
                SensorClusterEntry(plant_id=4, temperature=21.0, soil_moisture=45.0),
            ],
        )
        await cache.cache_command(cmd)

        rows = await cache.db.get_unsynced("soil_readings")
        assert len(rows) == 4
        plant_ids = [r["plant_id"] for r in rows]
        assert plant_ids == [1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_replay_unsynced_ambient(self, cache):
        """replay_unsynced should send cached ambient rows and mark them synced."""
        await cache.db.save_reading(node_id=5, temperature=20.0, humidity=50.0)
        await cache.db.save_reading(node_id=5, temperature=21.0, humidity=51.0)

        mock_ws = AsyncMock()
        await cache.replay_unsynced(mock_ws)

        assert mock_ws.send_json.call_count == 2
        # Verify payload structure
        first_call = mock_ws.send_json.call_args_list[0][0][0]
        assert first_call["type"] == "temp_hum_report"
        assert first_call["temperature"] == 20.0

        # All should be marked synced now
        remaining = await cache.db.get_unsynced("sensor_readings")
        assert len(remaining) == 0

    @pytest.mark.asyncio
    async def test_replay_unsynced_soil(self, cache):
        """replay_unsynced should send cached soil rows and mark them synced."""
        await cache.db.save_cluster_reading(plant_id=1, soil_temperature=18.0, soil_moisture=70.0)
        await cache.db.save_cluster_reading(plant_id=2, soil_temperature=19.0, soil_moisture=65.0)

        mock_ws = AsyncMock()
        await cache.replay_unsynced(mock_ws)

        assert mock_ws.send_json.call_count == 2
        first_call = mock_ws.send_json.call_args_list[0][0][0]
        assert first_call["type"] == "sensor_cluster_report"
        assert first_call["entries"][0]["plant_id"] == 1

        remaining = await cache.db.get_unsynced("soil_readings")
        assert len(remaining) == 0

    @pytest.mark.asyncio
    async def test_replay_stops_on_ws_failure(self, cache):
        """If WS send fails mid-replay, remaining rows stay unsynced."""
        for i in range(5):
            await cache.db.save_reading(node_id=1, temperature=20.0 + i, humidity=50.0)

        mock_ws = AsyncMock()
        # Fail on the 3rd call
        call_count = 0

        async def fail_on_third(payload):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                raise ConnectionError("WS disconnected")

        mock_ws.send_json.side_effect = fail_on_third
        await cache.replay_unsynced(mock_ws)

        # Only first 2 should be synced, 3 remain unsynced
        remaining = await cache.db.get_unsynced("sensor_readings")
        assert len(remaining) == 3


# ── Phase 5: End-to-end orchestrator integration ─────────────────────────


class TestOrchestratorIntegration:
    """
    Simulates the full flow: ESP32 → binary frame → UART buffer → parse →
    GatewayOrchestrator dispatches → caches locally + forwards to WS.
    """

    @pytest.mark.asyncio
    async def test_cluster_report_uart_to_cache_and_ws(self, orchestrator):
        """
        Simulate a sensor_cluster_report arriving from UART:
        the orchestrator should cache it AND forward via WS.
        """
        await orchestrator.cache.db.init_db()

        report = SensorClusterReport(
            target_id=1, source_id=2, node_id=2,
            entries=[
                SensorClusterEntry(plant_id=1, temperature=22.5, soil_moisture=68.0),
                SensorClusterEntry(plant_id=2, temperature=23.1, soil_moisture=55.5),
                SensorClusterEntry(plant_id=3, temperature=19.8, soil_moisture=72.3),
                SensorClusterEntry(plant_id=4, temperature=21.0, soil_moisture=45.0),
            ],
        )

        # This is what the UART dispatch_loop calls
        await orchestrator.dispatch_uart_to_ws(report)

        # 1. Verify WS forwarding
        orchestrator.ws_client.send_json.assert_called_once()
        ws_payload = orchestrator.ws_client.send_json.call_args[0][0]
        assert ws_payload["type"] == "sensor_cluster_report"
        assert len(ws_payload["entries"]) == 4

        # 2. Verify local SQLite cache
        rows = await orchestrator.cache.db.get_unsynced("soil_readings")
        assert len(rows) == 4
        assert rows[0]["plant_id"] == 1
        assert rows[0]["soil_temperature"] == 22.5
        assert rows[0]["soil_moisture"] == 68.0

    @pytest.mark.asyncio
    async def test_ambient_report_uart_to_cache_and_ws(self, orchestrator):
        """Ambient report should cache and forward."""
        await orchestrator.cache.db.init_db()

        report = TempHumReport(
            target_id=1, source_id=3, node_id=3,
            temperature=25.0, humidity=60.0,
        )
        await orchestrator.dispatch_uart_to_ws(report)

        orchestrator.ws_client.send_json.assert_called_once()
        rows = await orchestrator.cache.db.get_unsynced("sensor_readings")
        assert len(rows) == 1
        assert rows[0]["temperature"] == 25.0

    @pytest.mark.asyncio
    async def test_full_binary_flow_4_sensors(self, orchestrator, protocol):
        """
        Full simulation: build binary frame like the ESP32 sensor_cluster
        firmware does → parse it → dispatch through orchestrator → verify
        cache + WS.
        """
        await orchestrator.cache.db.init_db()

        # 1. Build the same report the ESP32 firmware would send
        original = SensorClusterReport(
            target_id=1, source_id=2, node_id=2,
            entries=[
                SensorClusterEntry(plant_id=1, temperature=22.50, soil_moisture=68.00),
                SensorClusterEntry(plant_id=2, temperature=23.10, soil_moisture=55.50),
                SensorClusterEntry(plant_id=3, temperature=19.80, soil_moisture=72.30),
                SensorClusterEntry(plant_id=4, temperature=21.00, soil_moisture=45.00),
            ],
        )

        # 2. Serialize to binary (what leaves the ESP32 over ESP-NOW → UART)
        frame = protocol.pack_frame(original)

        # 3. Parse the binary (what UartProcessor.process_buffer does)
        parsed = protocol.parse_frame(frame)
        assert parsed is not None
        assert isinstance(parsed, SensorClusterReport)

        # 4. Dispatch through orchestrator (what the UART listener triggers)
        await orchestrator.dispatch_uart_to_ws(parsed)

        # 5. Verify the whole chain worked
        # WS got the forwarded message
        orchestrator.ws_client.send_json.assert_called_once()
        ws_payload = orchestrator.ws_client.send_json.call_args[0][0]
        assert ws_payload["type"] == "sensor_cluster_report"
        assert len(ws_payload["entries"]) == 4

        # SQLite cached all 4 plant readings
        rows = await orchestrator.cache.db.get_unsynced("soil_readings")
        assert len(rows) == 4

        # CSV file was created
        today = datetime.now().strftime("%Y-%m-%d")
        csv_path = os.path.join(
            orchestrator.cache.csv.csv_dir, f"telemetry_{today}.csv"
        )
        assert os.path.exists(csv_path)
        with open(csv_path) as f:
            lines = f.readlines()
        assert len(lines) == 5  # header + 4 entries

    @pytest.mark.asyncio
    async def test_offline_cache_then_replay(self, orchestrator, protocol):
        """
        Simulate offline scenario:
        1. WS is down → telemetry still cached locally via direct cache call
        2. WS reconnects → replay_unsynced sends all cached data
        """
        await orchestrator.cache.db.init_db()

        # 1. Simulate offline: cache data directly (as the cache layer does)
        report = SensorClusterReport(
            target_id=1, source_id=2, node_id=2,
            entries=[
                SensorClusterEntry(plant_id=1, temperature=22.5, soil_moisture=68.0),
                SensorClusterEntry(plant_id=2, temperature=23.1, soil_moisture=55.5),
            ],
        )
        await orchestrator.cache.cache_command(report)

        # Data is in local cache
        rows = await orchestrator.cache.db.get_unsynced("soil_readings")
        assert len(rows) == 2

        # 2. Simulate WS reconnect — replay sends cached data
        mock_ws = AsyncMock()
        await orchestrator.cache.replay_unsynced(mock_ws)

        # Replay should have sent 2 messages
        assert mock_ws.send_json.call_count == 2

        # All rows marked synced
        remaining = await orchestrator.cache.db.get_unsynced("soil_readings")
        assert len(remaining) == 0

    @pytest.mark.asyncio
    async def test_on_ws_connect_replays(self, orchestrator):
        """_on_ws_connect should report config AND replay cached data."""
        await orchestrator.cache.db.init_db()

        # Pre-cache some data
        await orchestrator.cache.db.save_reading(
            node_id=3, temperature=25.0, humidity=60.0
        )

        orchestrator.device_manager.get_config.return_value = {"pump": {}}
        orchestrator.ws_client.send_json = AsyncMock()

        await orchestrator._on_ws_connect()

        # Should have sent: 1 system_config + 1 replayed ambient reading
        assert orchestrator.ws_client.send_json.call_count == 2
        calls = [c[0][0] for c in orchestrator.ws_client.send_json.call_args_list]
        types = [c["type"] for c in calls]
        assert "system_config" in types
        assert "temp_hum_report" in types

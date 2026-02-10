import pytest
import asyncio
import os
import shutil
import aiosqlite
from datetime import datetime

# Hack to import from src
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proyecto_demeter.data.database import DatabaseManager
from proyecto_demeter.data.file_logger import SensorLogger
from proyecto_demeter.core.async_service import DemeterService

# Mock for Protocol/Cmd
from pydantic import BaseModel

# Mock for Protocol/Cmd
class MockDataReport(BaseModel):
    node_id: int
    temperature: float
    humidity: float
    
    def get_cmd_id(self):
        return 0x0B # DataReport

@pytest.mark.asyncio
async def test_database_manager():
    """Test Data Manager Init and Save/Read"""
    db_path = "test_data.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    dm = DatabaseManager(db_path)
    await dm.init_db()
    
    # Save
    await dm.save_reading(1, 25.5, 60.0)
    await dm.save_reading(1, 26.0, 55.0)
    
    # Check
    rows = await dm.get_recent_readings(5)
    assert len(rows) == 2
    assert rows[0]['temperature'] == 26.0 # Ordered DESC
    
    # Check Stats
    stats = await dm.get_stats(1)
    assert stats['avg_temp'] == 25.75
    assert stats['min_temp'] == 25.5
    assert stats['max_temp'] == 26.0
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

def test_sensor_logger():
    """Test Sensor Logger"""
    log_dir = "test_logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Force fresh logger by removing handlers if present (Singleton issue)
    logger = SensorLogger(log_dir, "test_sensors.log")
    if logger.logger.handlers:
         for h in logger.logger.handlers[:]:
             logger.logger.removeHandler(h)
         # Re-init manually to ensure correct file
         import logging.handlers
         h = logging.handlers.RotatingFileHandler(logger.filepath, maxBytes=1000, backupCount=1)
         h.setFormatter(logging.Formatter('%(asctime)s,%(message)s'))
         logger.logger.addHandler(h)
    
    filepath = logger.get_log_path()
    
    logger.log_reading(2, 22.2, 44.4)
    
    # Verify File Content
    with open(filepath, "r") as f:
        content = f.read()
        assert "2,22.20,44.40" in content
        
    # Cleanup (rmtree or file)
    # Close handlers to release file lock
    if hasattr(logger, 'logger'):
        for h in logger.logger.handlers:
            h.close()
            logger.logger.removeHandler(h)
    
    if os.path.exists(log_dir):
        try:
            shutil.rmtree(log_dir)
        except Exception as e:
            print(f"Cleanup Error: {e}")

@pytest.mark.asyncio
async def test_service_integration():
    """Test DemeterService Data Flow"""
    # Setup Service with Test DB
    service = DemeterService()
    service.data_manager = DatabaseManager("test_service.db")
    await service.data_manager.init_db()
    
    # Setup Logger
    service.sensor_logger = SensorLogger("test_logs", "service_test.log")
    
    # Mock Protocol Command
    cmd = MockDataReport(node_id=99, temperature=12.3, humidity=88.8)
    
    # Execute Handler (Async)
    await service.handle_protocol_command(cmd)
    
    # Assertion: Check DB
    rows = await service.data_manager.get_recent_readings(1)
    assert len(rows) == 1
    assert rows[0]['node_id'] == 99
    assert rows[0]['temperature'] == 12.3
    
    # Cleanup
    if os.path.exists("test_service.db"):
        os.remove("test_service.db")
    if os.path.exists("test_logs/service_test.log"):
        os.remove("test_logs/service_test.log")
        os.rmdir("test_logs")


import pytest
import os
import shutil
from pathlib import Path
from utils.logger import SystemLogger, sys_logger
from config.config import config

@pytest.fixture
def clean_logs():
    # Setup: Clean logs dir
    if config.SESSION_LOG_DIR.exists():
        shutil.rmtree(config.SESSION_LOG_DIR)
    yield
    # Teardown: Clean again (optional)

def test_logger_singleton():
    logger1 = SystemLogger()
    logger2 = SystemLogger()
    assert logger1 is logger2
    assert sys_logger is logger1

def test_logger_creates_session_file(clean_logs):
    # Initializes logger
    sys_logger.setup()
    
    # Check directory exists
    assert config.SESSION_LOG_DIR.exists()
    
    # Check file created
    files = list(config.SESSION_LOG_DIR.glob("session_*.log"))
    assert len(files) == 1

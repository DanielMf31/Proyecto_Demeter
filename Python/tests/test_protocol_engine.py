
import pytest
from unittest.mock import MagicMock
import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from protocol_engine import ProtocolEngine, CODIGO_SOLICITUD_CONEXION, CODIGO_CONFIRMACION_CONEXION

class TestProtocolEngine:
    @pytest.fixture
    def mock_uart(self):
        return MagicMock()

    def test_initial_state(self, mock_uart):
        engine = ProtocolEngine(mock_uart)
        assert engine.state == 0 # ESTADO_INICIAL

    def test_start_protocol_sends_101(self, mock_uart):
        engine = ProtocolEngine(mock_uart)
        engine.start_protocol()
        
        mock_uart.send.assert_called_with(str(CODIGO_SOLICITUD_CONEXION))
        assert engine.state == 1 # ESPERANDO_CONFIRMACION_102

    def test_process_receive_102_triggers_transmission(self, mock_uart):
        engine = ProtocolEngine(mock_uart)
        engine.configure_data([[1,1,1,1,1]] * 5)
        
        # Setup state to waiting 102
        engine.state = 1
        
        # Mock receiving '102'
        mock_uart.receive.side_effect = ["102", None] 
        
        engine.process()
        
        # Should have sent the data (5 times)
        assert mock_uart.send.call_count == 5 
        # State should be waiting for 103 (actually 3)
        assert engine.state == 3 # ESPERANDO_103_Y_DATOS

    def test_process_verification_success(self, mock_uart):
        engine = ProtocolEngine(mock_uart)
        test_data = [
            [1, 1, 0, 1000, 0],
            [1, 2, 0, 2000, 0],
            [1, 3, 0, 3000, 0],
            [1, 4, 0, 4000, 0],
            [1, 5, 0, 5000, 0]
        ]
        engine.configure_data(test_data)
        
        # Setup: We sent data and are waiting for 103
        engine.state = 3 
        
        # Sequence of messages: 103, then the 5 echoes
        side_effects = ["103"]
        for cmd in test_data:
            side_effects.append(" ".join(map(str, cmd)))
        side_effects.append(None) # End of messages
        
        mock_uart.receive.side_effect = side_effects
        
        # Run process cycle
        # We might need multiple calls or loop if process consumes one at a time?
        # The process() implementation has a while loop, so one call should drain the side_effects
        engine.process()
        
        # Check success
        # Should verify and send 104
        mock_uart.send.assert_any_call("104")
        assert engine.state == 5 # COMUNICACION_COMPLETADA

    def test_process_verification_failure(self, mock_uart):
        engine = ProtocolEngine(mock_uart)
        test_data = [[1, 1, 0, 1000, 0]] * 5
        engine.configure_data(test_data)
        
        engine.state = 3
        
        # Sequence: 103, then WRONG echoes
        side_effects = ["103"]
        wrong_data = [9, 9, 9, 9, 9] # Mismatch
        for _ in range(5):
            side_effects.append(" ".join(map(str, wrong_data)))
        side_effects.append(None)
        
        mock_uart.receive.side_effect = side_effects
        
        engine.process()
        
        # Should fail and send 105
        mock_uart.send.assert_any_call("105")
        assert engine.state == 6 # ERROR_COMUNICACION

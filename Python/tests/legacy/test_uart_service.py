
import pytest
from unittest.mock import MagicMock, patch

from src.uart_service import UARTService


class TestUARTService:
    @patch('serial.Serial')
    def test_connect_success(self, mock_serial):
        # Setup mock
        mock_serial.return_value.is_open = True
        
        service = UARTService(port='/dev/test', baudrate=9600)
        result = service.connect()
        
        assert result is True
        mock_serial.assert_called_with(
            port='/dev/test',
            baudrate=9600,
            timeout=1,
            bytesize=8,
            parity='N',
            stopbits=1
        )
        assert service.serial_connection is not None

    @patch('serial.Serial')
    def test_connect_fail(self, mock_serial):
        # Simulate exception
        import serial
        mock_serial.side_effect = serial.SerialException("Error")
        
        service = UARTService()
        result = service.connect()
        
        assert result is False
        assert service.serial_connection is None

    def test_send_success(self):
        service = UARTService()
        service.serial_connection = MagicMock()
        service.serial_connection.is_open = True
        
        result = service.send("HELLO")
        
        assert result is True
        # Verifica que añade el newline y encodea
        service.serial_connection.write.assert_called_with(b'HELLO\n')

    def test_receive(self):
        service = UARTService()
        service.serial_connection = MagicMock()
        service.serial_connection.is_open = True
        service.serial_connection.in_waiting = 10
        # Simular lectura de bytes
        service.serial_connection.readline.return_value = b'RESPONSE \n'
        
        result = service.receive()
        
        assert result == "RESPONSE"

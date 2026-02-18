from ..manager import manager
from Core.logger import setup_logger

logger = setup_logger("ws_commands")

async def send_command_to_device(client_id: str, command: str, params: dict = {}):
    """
    Send a command to a specific device via WebSocket.
    """
    logger.info(f"Sending command '{command}' to {client_id}")
    message = {
        "type": "command",
        "command": command,
        "params": params
    }
    await manager.send_personal_message(message, client_id)

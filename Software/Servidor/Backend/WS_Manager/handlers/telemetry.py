from Core.logger import setup_logger

logger = setup_logger("ws_telemetry")

async def handle_telemetry(data: dict, client_id: str):
    """
    Process telemetry data from the Raspberry Pi.
    Store in DB, InfluxDB, or just log for now.
    """
    logger.info(f"Processing telemetry from {client_id}: {data}")
    # TODO: Parse data and save to DB

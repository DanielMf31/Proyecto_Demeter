import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Importación de tareas
from tasks import sync_sensor_data_to_redis, dummy_insert_test_data, enqueue_nightly_etl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("secuenciador_main")

async def main():
    logger.info("=========================================")
    logger.info(" Iniciando DEMETER SECUENCIADOR (APScheduler) ")
    logger.info("=========================================")
    
    scheduler = AsyncIOScheduler()
    
    # 1. Job Horario (Sync PostgreSQL -> Redis Caché)
    scheduler.add_job(sync_sensor_data_to_redis, 'cron', minute=0)
    
    # 2. Job Media Hora (Demo: Generación de mediciones fake para test visual)
    scheduler.add_job(dummy_insert_test_data, 'interval', minutes=30)
    
    # 3. Job Madrugada (3:00 AM) (Recalcular y Cachear datos analíticos en Redis)
    scheduler.add_job(enqueue_nightly_etl, 'cron', hour=3, minute=0)
    
    scheduler.start()
    logger.info("Schedulers activos. A la espera de eventos...")
    
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Apagando Secuenciador...")

if __name__ == "__main__":
    asyncio.run(main())

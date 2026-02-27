import asyncio
import logging
import json
import math
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Fix ModuleNotFoundError within Docker
sys.path.insert(0, '/app/Software/Common')
sys.path.insert(0, '/app/Software/Servidor/Backend')

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from Core.database import AsyncSessionLocal
from Core.auth import get_password_hash
from BD.models import User, Experiment, Plant, TelemetryTH, ExperimentoPlantaLink
from Core.redis import redis_manager

logger = logging.getLogger("seed_data")
logging.basicConfig(level=logging.INFO)

# ─────────────────────────────────────────────────────────────────────────────
# Definición de las 4 especies con 5 variedades cada una (20 plantas)
# ─────────────────────────────────────────────────────────────────────────────
SPECIES_CATALOG = [
    # Tomates (5)
    {"name": "Tomate Cherry-001",     "id_fisico": "TOM-001", "especie": "Solanum lycopersicum",  "variedad": "Cherry"},
    {"name": "Tomate Raf-002",        "id_fisico": "TOM-002", "especie": "Solanum lycopersicum",  "variedad": "Raf"},
    {"name": "Tomate Kumato-003",     "id_fisico": "TOM-003", "especie": "Solanum lycopersicum",  "variedad": "Kumato"},
    {"name": "Tomate Pera-004",       "id_fisico": "TOM-004", "especie": "Solanum lycopersicum",  "variedad": "Pera"},
    {"name": "Tomate Corazón-005",    "id_fisico": "TOM-005", "especie": "Solanum lycopersicum",  "variedad": "Corazón de Buey"},
    # Patatas (5)
    {"name": "Patata Kennebec-001",   "id_fisico": "PAT-001", "especie": "Solanum tuberosum",     "variedad": "Kennebec"},
    {"name": "Patata Agria-002",      "id_fisico": "PAT-002", "especie": "Solanum tuberosum",     "variedad": "Agria"},
    {"name": "Patata Monalisa-003",   "id_fisico": "PAT-003", "especie": "Solanum tuberosum",     "variedad": "Monalisa"},
    {"name": "Patata Spunta-004",     "id_fisico": "PAT-004", "especie": "Solanum tuberosum",     "variedad": "Spunta"},
    {"name": "Patata Red Pontiac-005","id_fisico": "PAT-005", "especie": "Solanum tuberosum",     "variedad": "Red Pontiac"},
    # Lechugas (5)
    {"name": "Lechuga Romana-001",    "id_fisico": "LEC-001", "especie": "Lactuca sativa",        "variedad": "Romana"},
    {"name": "Lechuga Iceberg-002",   "id_fisico": "LEC-002", "especie": "Lactuca sativa",        "variedad": "Iceberg"},
    {"name": "Lechuga Batavia-003",   "id_fisico": "LEC-003", "especie": "Lactuca sativa",        "variedad": "Batavia"},
    {"name": "Lechuga Lollo-004",     "id_fisico": "LEC-004", "especie": "Lactuca sativa",        "variedad": "Lollo Rosso"},
    {"name": "Lechuga Hoja Roble-005","id_fisico": "LEC-005", "especie": "Lactuca sativa",        "variedad": "Hoja de Roble"},
    # Berenjenas (5)
    {"name": "Berenjena Listada-001", "id_fisico": "BER-001", "especie": "Solanum melongena",     "variedad": "Listada de Gandía"},
    {"name": "Berenjena Larga-002",   "id_fisico": "BER-002", "especie": "Solanum melongena",     "variedad": "Larga Negra"},
    {"name": "Berenjena Redonda-003", "id_fisico": "BER-003", "especie": "Solanum melongena",     "variedad": "Redonda Negra"},
    {"name": "Berenjena Blanca-004",  "id_fisico": "BER-004", "especie": "Solanum melongena",     "variedad": "Blanca"},
    {"name": "Berenjena Thai-005",    "id_fisico": "BER-005", "especie": "Solanum melongena",     "variedad": "Thai Green"},
]

EXPERIMENT_CONFIGS = [
    {"name": "Ensayo Estrés Salino",  "desc": "Evaluación respuesta a alta conductividad eléctrica", "rango": (0, 8)},
    {"name": "Ensayo Lumínico",       "desc": "Fotoperiodo extendido 18h luz / 6h oscuridad",       "rango": (6, 14)},
    {"name": "Control General",       "desc": "Grupo de control condiciones estándar",               "rango": (12, 20)},
]


async def seed_historical_data(db: AsyncSession):
    """
    Inyecta datos históricos (6 meses) simulando una arquitectura LIMS.
    20 Plantas (4 especies × 5 variedades) → 3 Experimentos entrelazados.
    Guarda telemetría en Postgres y cachea por planta en Redis para lectura inmediata.
    También inyecta telemetría cruda para graficación con Pandas (Dióxido de Carbono virtual, 
    Humedad, Temperatura ambiental de invernadero).
    
    :param db: Sesión AsyncSession inyectada en tiempo de ejecución.
    """
    logger.info("Verificando/Creando Usuario Admin...")
    
    result = await db.execute(select(User).where(User.username == "admin"))
    admin = result.scalars().first()
    if not admin:
        admin = User(
            username="admin", 
            password_hash=get_password_hash("admin"), 
            role="admin"
        )
        db.add(admin)
        await db.flush()
        logger.info("Usuario 'admin' creado.")

    logger.info("Limpiando datos de prueba anteriores...")
    await db.execute(delete(ExperimentoPlantaLink))
    await db.execute(delete(TelemetryTH))
    await db.execute(delete(Plant))
    await db.execute(delete(Experiment))
    await db.commit()

    # ─── Crear 20 Plantas ─────────────────────────────────────────────────────
    logger.info("Creando 20 Plantas LIMS (4 especies × 5 variedades)...")
    plantas = []
    fecha_base = datetime.utcnow().date() - timedelta(days=200)
    
    for i, spec in enumerate(SPECIES_CATALOG, start=1):
        p = Plant(
            name=spec["name"],
            identificador_fisico=spec["id_fisico"],
            especie_variedad=spec["especie"],
            fecha_siembra=fecha_base + timedelta(days=(i % 7) * 3),
            estado_vital="Activa",
            metadata_cientifica={
                "variedad": spec["variedad"],
                "sustrato": "Fibra de Coco 70/30" if i % 2 == 0 else "Perlita/Vermiculita 50/50",
                "iluminacion": "LED 600W Full Spectrum" if i <= 10 else "HPS 400W",
                "ce_objetivo": round(1.8 + (i % 5) * 0.15, 2),
                "ph_objetivo": round(5.5 + (i % 3) * 0.2, 1),
                "ubicacion": f"Invernadero {chr(65 + i % 4)} - Mesa {(i % 5) + 1}",
            },
            node_id=i
        )
        db.add(p)
        plantas.append(p)
    await db.flush()

    # ─── Crear 3 Experimentos ─────────────────────────────────────────────────
    logger.info("Creando Experimentos y cruzando Plantas (Many-to-Many)...")
    experimentos = []
    
    for idx, cfg in enumerate(EXPERIMENT_CONFIGS, start=1):
        exp = Experiment(
            name=cfg["name"],
            description=cfg["desc"],
            user_id=admin.id,
            api_key=f"DEMETER-EXP-{idx}-SECRET-KEY"
        )
        db.add(exp)
        await db.flush()
        experimentos.append(exp)
        
        start_idx, end_idx = cfg["rango"]
        for p in plantas[start_idx:end_idx]:
            link = ExperimentoPlantaLink(experiment_id=exp.id, plant_id=p.id)
            db.add(link)
            
    await db.flush()
    await db.commit()

    # ─── Generar 6 meses (180 días) de telemetría ─────────────────────────────
    logger.info("Generando 6 meses (180 días) de telemetría usando NumPy...")
    num_plants = len(plantas)
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    start_date = now - timedelta(days=180)
    total_hours = 180 * 24  # 4320 horas
    
    await redis_manager.connect()
    
    # Pre-generar ruido gaussiano para todas las plantas
    t_noises = np.random.normal(0, 0.5, (num_plants, total_hours))
    h_noises = np.random.normal(0, 1.5, (num_plants, total_hours))
    
    # Diccionario para acumular telemetría por planta
    telemetry_by_plant: dict[int, list[dict]] = {p.id: [] for p in plantas}
    records: list[TelemetryTH] = []
    
    for hour in range(total_hours):
        current_time = start_date + timedelta(hours=hour)
        time_str = current_time.isoformat()
        
        # Ciclo diurno sinusoidal
        diurnal_cycle = math.cos((current_time.hour - 14) * math.pi / 12)
        t_base = 22.5 + diurnal_cycle * 7.5
        hr_base = 62.5 - diurnal_cycle * 22.5
        
        for p_idx, p in enumerate(plantas):
            temp_final = round(max(10.0, min(40.0, t_base + t_noises[p_idx][hour])), 2)
            hr_final = round(max(10.0, min(100.0, hr_base + h_noises[p_idx][hour])), 2)
            
            records.append(TelemetryTH(
                timestamp=current_time,
                node_id=p.node_id,
                temperature=temp_final,
                humidity=hr_final
            ))
            
            telemetry_by_plant[p.id].append({
                "timestamp": time_str,
                "node_id": p.node_id,
                "temperature": temp_final,
                "humidity": hr_final
            })
            
            # Flush por lotes para no saturar la RAM
            if len(records) >= 10000:
                db.add_all(records)
                await db.commit()
                records = []
                
    if records:
        db.add_all(records)
        await db.commit()
        
    # ─── Cachear en Redis POR PLANTA ──────────────────────────────────────────
    logger.info("Guardando caché Redis por planta (demeter:plant_telemetry:{id})...")
    if redis_manager.redis:
        for p in plantas:
            cache_key = f"demeter:plant_telemetry:{p.id}"
            data = telemetry_by_plant[p.id]
            logger.info(f" -> {cache_key}: {len(data)} registros")
            await redis_manager.redis.set(cache_key, json.dumps(data))

    # ─── También cachear por experimento (compatibilidad) ─────────────────────
    logger.info("Guardando Vistas Materializadas en Redis por Experimento...")
    if redis_manager.redis:
        for idx, cfg in enumerate(EXPERIMENT_CONFIGS):
            start_idx, end_idx = cfg["rango"]
            exp_plants = plantas[start_idx:end_idx]
            
            exp_cache_data = []
            for p in exp_plants:
                exp_cache_data.extend(telemetry_by_plant[p.id])
            
            cache_key = f"demeter:raw_data:experimento_{experimentos[idx].id}"
            logger.info(f" -> Guardando {len(exp_cache_data)} registros crudos en {cache_key}")
            await redis_manager.redis.set(cache_key, json.dumps(exp_cache_data))
            
    logger.info("Proceso de Seeding LIMM (Fase 9) Completado exitosamente!")
    
    if redis_manager.redis:
        await redis_manager.close()

async def main():
    async with AsyncSessionLocal() as session:
        await seed_historical_data(session)

if __name__ == "__main__":
    asyncio.run(main())

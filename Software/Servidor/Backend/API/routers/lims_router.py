import logging
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from Core.database import get_db
from Core.redis import redis_manager
from Core.auth import get_current_active_user
from BD.models import Experiment, User, Plant, ExperimentoPlantaLink, PlantSensorMap
from BD.schemas import (
    PlantCreate, PlantUpdate, PlantResponse,
    ExperimentCreate, ExperimentResponse,
    PlantSensorMapCreate, PlantSensorMapResponse,
)

logger = logging.getLogger("lims_router")
router = APIRouter(prefix="/lims", tags=["LIMS Architecture"])

# ─────────────────────────────────────────────────────────────────────────────
# PLANTS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/plantas", response_model=List[PlantResponse])
async def get_plantas(db: AsyncSession = Depends(get_db)):
    """Retrieve all physical plants registered in the LIMS."""
    result = await db.execute(select(Plant).order_by(Plant.id))
    plants = result.scalars().all()
    return plants

@router.get("/plantas/{plant_id}", response_model=PlantResponse)
async def get_planta_detail(plant_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a single plant with its associated experiments."""
    stmt = select(Plant).options(selectinload(Plant.experiments)).where(Plant.id == plant_id)
    result = await db.execute(stmt)
    plant = result.scalar_one_or_none()
    if not plant:
        raise HTTPException(status_code=404, detail=f"Plant with id={plant_id} not found")
    return plant

@router.patch("/plantas/{plant_id}", response_model=PlantResponse)
async def update_planta(plant_id: int, plant_in: PlantUpdate, db: AsyncSession = Depends(get_db)):
    """Partially update a plant's metadata and properties."""
    stmt = select(Plant).where(Plant.id == plant_id)
    result = await db.execute(stmt)
    plant = result.scalar_one_or_none()
    if not plant:
        raise HTTPException(status_code=404, detail=f"Plant with id={plant_id} not found")

    update_data = plant_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plant, field, value)

    try:
        await db.commit()
        await db.refresh(plant)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")
    return plant

@router.get("/plantas/{plant_id}/telemetry")
async def get_plant_telemetry(plant_id: int):
    """
    Fetch 6-month telemetry for a plant directly from Redis cache.
    Zero database queries — instant response.
    """
    cache_key = f"demeter:plant_telemetry:{plant_id}"
    
    if not redis_manager.redis:
        await redis_manager.connect()
    
    cached = await redis_manager.redis.get(cache_key)
    if not cached:
        raise HTTPException(
            status_code=404, 
            detail=f"No telemetry cache found for plant_id={plant_id}. Run the seeder first."
        )
    
    data = json.loads(cached)
    return data

@router.post("/plantas", response_model=PlantResponse)
async def create_planta(plant_in: PlantCreate, db: AsyncSession = Depends(get_db)):
    """Register a new physical plant with rich biological metadata."""
    result = await db.execute(select(Plant).where(Plant.identificador_fisico == plant_in.identificador_fisico))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Plant with this 'identificador_fisico' already exists.")
        
    db_plant = Plant(
        name=plant_in.name,
        identificador_fisico=plant_in.identificador_fisico,
        especie_variedad=plant_in.especie_variedad,
        fecha_siembra=plant_in.fecha_siembra,
        estado_vital=plant_in.estado_vital,
        metadata_cientifica=plant_in.metadata_cientifica,
        node_id=plant_in.node_id
    )
    db.add(db_plant)
    try:
        await db.commit()
        await db.refresh(db_plant)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    
    return db_plant

# ─────────────────────────────────────────────────────────────────────────────
# EXPERIMENTS
# ── EXPERIMENTOS ─────────────────────────────────────────────────────────────

@router.get("/experimentos", response_model=List[ExperimentResponse])
async def get_experimentos(db: AsyncSession = Depends(get_db)):
    """List all experiments and the plants associated with them."""
    stmt = select(Experiment).options(selectinload(Experiment.plants)).order_by(Experiment.id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/experimentos/generar", response_model=ExperimentResponse)
async def generar_experimento(exp_in: ExperimentCreate, db: AsyncSession = Depends(get_db)):
    """Generate a new experiment wrapping multiple plants."""
    if exp_in.plant_ids:
        query = select(Plant).where(Plant.id.in_(exp_in.plant_ids))
        result = await db.execute(query)
        found_plants = result.scalars().all()
        if len(found_plants) != len(exp_in.plant_ids):
            raise HTTPException(status_code=404, detail="One or more Plant IDs not found")
    else:
        found_plants = []
        
    db_exp = Experiment(
        name=exp_in.name,
        description=exp_in.description
    )
    
    db.add(db_exp)
    await db.commit()
    await db.refresh(db_exp)
    
    for plant in found_plants:
        link = ExperimentoPlantaLink(
            experiment_id=db_exp.id,
            plant_id=plant.id
        )
        db.add(link)
        
    if found_plants:
        await db.commit()
        
    stmt = select(Experiment).options(selectinload(Experiment.plants)).where(Experiment.id == db_exp.id)
    final_result = await db.execute(stmt)
    return final_result.scalar_one()


# ─────────────────────────────────────────────────────────────────────────────
# SENSOR MAP (node_id, sensor_slot) → plant_id
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/sensor-map", response_model=List[PlantSensorMapResponse])
async def get_sensor_mappings(db: AsyncSession = Depends(get_db)):
    """List all sensor-slot-to-plant mappings."""
    stmt = (
        select(PlantSensorMap)
        .options(selectinload(PlantSensorMap.plant))
        .order_by(PlantSensorMap.node_id, PlantSensorMap.sensor_slot)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/sensor-map", response_model=PlantSensorMapResponse)
async def upsert_sensor_mapping(
    mapping_in: PlantSensorMapCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_active_user),
):
    """Create or update a sensor-slot-to-plant mapping (upsert)."""
    # Verify plant exists
    plant = await db.execute(select(Plant).where(Plant.id == mapping_in.plant_id))
    if not plant.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Plant id={mapping_in.plant_id} not found")

    # Check for existing mapping on this (node_id, sensor_slot)
    stmt = select(PlantSensorMap).where(
        PlantSensorMap.node_id == mapping_in.node_id,
        PlantSensorMap.sensor_slot == mapping_in.sensor_slot,
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.plant_id = mapping_in.plant_id
    else:
        existing = PlantSensorMap(**mapping_in.model_dump())
        db.add(existing)

    await db.commit()
    await db.refresh(existing)
    return existing


@router.delete("/sensor-map/{mapping_id}", status_code=204)
async def delete_sensor_mapping(
    mapping_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_active_user),
):
    """Remove a sensor-slot mapping."""
    result = await db.execute(select(PlantSensorMap).where(PlantSensorMap.id == mapping_id))
    mapping = result.scalar_one_or_none()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    await db.delete(mapping)
    await db.commit()

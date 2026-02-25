from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Index, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Import Base from Core.database so we use the same declarative base
from Core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)

    # Soft Delete logic would typically be handled in the CRUD layer or via a custom method/mixin
    # interactions
    sequences = relationship("Sequence", back_populates="creator")
    activity_logs = relationship("ActivityLog", back_populates="user")
    experiments = relationship("Experiment", back_populates="user")

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False) # 'pump', 'valve'
    gpio_pin = Column(Integer, nullable=False)

    # Relationships
    sequence_steps = relationship("SequenceStep", back_populates="device")
    activity_logs = relationship("ActivityLog", back_populates="device")

class Sequence(Base):
    __tablename__ = "sequences"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="sequences")
    steps = relationship("SequenceStep", back_populates="sequence", cascade="all, delete-orphan")

class SequenceStep(Base):
    __tablename__ = "sequence_steps"

    id = Column(Integer, primary_key=True, index=True)
    sequence_id = Column(Integer, ForeignKey("sequences.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    target_state = Column(Boolean, nullable=False)
    duration_seconds = Column(Integer, nullable=False)

    # Relationships
    sequence = relationship("Sequence", back_populates="steps")
    device = relationship("Device", back_populates="sequence_steps")

class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    action_type = Column(String, nullable=False) # 'button_press', 'sequence_exec', etc.
    description = Column(Text)

    # Relationships
    user = relationship("User", back_populates="activity_logs")
    device = relationship("Device", back_populates="activity_logs")

    # Index on timestamp as requested for performance
    __table_args__ = (
        Index('idx_activity_log_timestamp', 'timestamp'),
    )

class ExperimentoPlantaLink(Base):
    __tablename__ = "experimento_planta_link"
    
    experiment_id = Column(Integer, ForeignKey("experiments.id", ondelete="CASCADE"), primary_key=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"), primary_key=True)
    linked_at = Column(DateTime, default=datetime.utcnow)

class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    api_key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    user = relationship("User", back_populates="experiments")
    plants = relationship("Plant", secondary="experimento_planta_link", back_populates="experiments")

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    # LIMS Physical Identifiers & Biology
    identificador_fisico = Column(String, unique=True, index=True, nullable=False)
    especie_variedad = Column(String, nullable=False)
    fecha_siembra = Column(Date, nullable=False)
    estado_vital = Column(String, default="Activa", nullable=False) # e.g., Activa, Cosechada, Muerta
    metadata_cientifica = Column(JSONB, nullable=False, default={})
    
    node_id = Column(Integer, unique=True, nullable=False) 
    
    experiments = relationship("Experiment", secondary="experimento_planta_link", back_populates="plants")

# --- Telemetry Models ---


class TelemetryTH(Base):
    __tablename__ = "telemetry_th"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    node_id = Column(Integer, nullable=False, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)

class PinHistory(Base):
    __tablename__ = "pin_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    node_id = Column(Integer, nullable=False, index=True)
    pin = Column(Integer, nullable=False)
    state = Column(Boolean, nullable=False)

class SystemHistory(Base):
    __tablename__ = "system_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    node_id = Column(Integer, nullable=False, index=True)
    mode = Column(Integer, nullable=False)
    battery_mv = Column(Integer, nullable=False)

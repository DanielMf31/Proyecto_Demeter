from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Index
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
    action_type = Column(String, nullable=False)
    description = Column(Text)

    # Relationships
    user = relationship("User", back_populates="activity_logs")
    device = relationship("Device", back_populates="activity_logs")

    # Index on timestamp as requested for performance
    __table_args__ = (
        Index('idx_activity_log_timestamp', 'timestamp'),
    )

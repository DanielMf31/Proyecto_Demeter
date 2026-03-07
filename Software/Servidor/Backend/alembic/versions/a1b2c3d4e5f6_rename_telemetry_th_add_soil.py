"""Rename telemetry_th to telemetry_ambient, add telemetry_soil

Revision ID: a1b2c3d4e5f6
Revises: eb2b85ec72b6
Create Date: 2026-03-08 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'eb2b85ec72b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename table telemetry_th -> telemetry_ambient
    op.rename_table('telemetry_th', 'telemetry_ambient')

    # 2. Rename columns: temperature -> air_temperature, humidity -> air_humidity
    op.alter_column('telemetry_ambient', 'temperature', new_column_name='air_temperature')
    op.alter_column('telemetry_ambient', 'humidity', new_column_name='air_humidity')

    # 3. Rename indexes to match new table name
    op.drop_index('ix_telemetry_th_id', table_name='telemetry_ambient')
    op.drop_index('ix_telemetry_th_node_id', table_name='telemetry_ambient')
    op.drop_index('ix_telemetry_th_timestamp', table_name='telemetry_ambient')
    op.create_index(op.f('ix_telemetry_ambient_id'), 'telemetry_ambient', ['id'], unique=False)
    op.create_index(op.f('ix_telemetry_ambient_node_id'), 'telemetry_ambient', ['node_id'], unique=False)
    op.create_index(op.f('ix_telemetry_ambient_timestamp'), 'telemetry_ambient', ['timestamp'], unique=False)

    # 4. Create telemetry_soil table
    op.create_table('telemetry_soil',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('plant_id', sa.Integer(), nullable=False),
        sa.Column('soil_temperature', sa.Float(), nullable=False),
        sa.Column('soil_moisture', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_telemetry_soil_id'), 'telemetry_soil', ['id'], unique=False)
    op.create_index(op.f('ix_telemetry_soil_plant_id'), 'telemetry_soil', ['plant_id'], unique=False)
    op.create_index(op.f('ix_telemetry_soil_timestamp'), 'telemetry_soil', ['timestamp'], unique=False)


def downgrade() -> None:
    # Drop telemetry_soil
    op.drop_index(op.f('ix_telemetry_soil_timestamp'), table_name='telemetry_soil')
    op.drop_index(op.f('ix_telemetry_soil_plant_id'), table_name='telemetry_soil')
    op.drop_index(op.f('ix_telemetry_soil_id'), table_name='telemetry_soil')
    op.drop_table('telemetry_soil')

    # Revert indexes
    op.drop_index(op.f('ix_telemetry_ambient_timestamp'), table_name='telemetry_ambient')
    op.drop_index(op.f('ix_telemetry_ambient_node_id'), table_name='telemetry_ambient')
    op.drop_index(op.f('ix_telemetry_ambient_id'), table_name='telemetry_ambient')

    # Rename columns back
    op.alter_column('telemetry_ambient', 'air_temperature', new_column_name='temperature')
    op.alter_column('telemetry_ambient', 'air_humidity', new_column_name='humidity')

    # Rename table back
    op.rename_table('telemetry_ambient', 'telemetry_th')

    # Recreate original indexes
    op.create_index(op.f('ix_telemetry_th_id'), 'telemetry_th', ['id'], unique=False)
    op.create_index(op.f('ix_telemetry_th_node_id'), 'telemetry_th', ['node_id'], unique=False)
    op.create_index(op.f('ix_telemetry_th_timestamp'), 'telemetry_th', ['timestamp'], unique=False)

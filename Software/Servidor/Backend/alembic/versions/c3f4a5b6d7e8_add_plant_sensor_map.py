"""Add plant_sensor_map table

Revision ID: c3f4a5b6d7e8
Revises: a1b2c3d4e5f6
Create Date: 2026-03-10 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c3f4a5b6d7e8'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('plant_sensor_map',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.Integer(), nullable=False),
        sa.Column('sensor_slot', sa.Integer(), nullable=False),
        sa.Column('plant_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plant_sensor_map_id'), 'plant_sensor_map', ['id'], unique=False)
    op.create_index(op.f('ix_plant_sensor_map_node_id'), 'plant_sensor_map', ['node_id'], unique=False)
    op.create_index('uq_node_slot', 'plant_sensor_map', ['node_id', 'sensor_slot'], unique=True)


def downgrade() -> None:
    op.drop_index('uq_node_slot', table_name='plant_sensor_map')
    op.drop_index(op.f('ix_plant_sensor_map_node_id'), table_name='plant_sensor_map')
    op.drop_index(op.f('ix_plant_sensor_map_id'), table_name='plant_sensor_map')
    op.drop_table('plant_sensor_map')

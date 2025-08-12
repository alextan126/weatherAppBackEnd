"""initial schema

Revision ID: 41ddd7b4ad9d
Revises: 
Create Date: 2025-08-11 20:06:01.659158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import date



# revision identifiers, used by Alembic.
revision: str = '41ddd7b4ad9d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # created by autogenerate — keep this
    op.create_table(
        'location',
        sa.Column('location_id', sa.BigInteger(), primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('country_code', sa.Text()),
        sa.Column('admin1', sa.Text()),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('external_source', sa.Text()),
        sa.Column('external_id', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # >>> replace the autogen'd weather_observation table with this parent + partitions:
    op.execute("""
        CREATE TABLE weather_observation (
            location_id  BIGINT NOT NULL REFERENCES location(location_id) ON DELETE CASCADE,
            ts           TIMESTAMPTZ NOT NULL,
            temp_c       NUMERIC(5,2) NOT NULL,
            source       TEXT,
            inserted_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (location_id, ts)
        ) PARTITION BY RANGE (ts);
    """)

    start_year, end_year = 1980, date.today().year + 1
    for y in range(start_year, end_year):
        op.execute(f"""
            CREATE TABLE IF NOT EXISTS weather_observation_{y}
            PARTITION OF weather_observation
            FOR VALUES FROM ('{y}-01-01') TO ('{y+1}-01-01');
        """)

def downgrade():
    from datetime import date
    start_year, end_year = 1980, date.today().year + 1
    for y in reversed(range(start_year, end_year)):
        op.execute(f"DROP TABLE IF EXISTS weather_observation_{y} CASCADE;")
    op.execute("DROP TABLE IF EXISTS weather_observation CASCADE;")

    # drop other tables created above
    op.drop_table('location')
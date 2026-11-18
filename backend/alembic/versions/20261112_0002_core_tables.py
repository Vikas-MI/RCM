"""Create core RCM tables.

Revision ID: 20261112_0002
Revises: 20261112_0001
Create Date: 2026-11-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20261112_0002"
down_revision: Union[str, None] = "20261112_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tables are also created via Base.metadata.create_all for learning speed.
    # This revision documents the Phase 3 schema intent.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "patients" in inspector.get_table_names():
        return
    # Fallback: let create_all handle it at app startup / seed.


def downgrade() -> None:
    pass

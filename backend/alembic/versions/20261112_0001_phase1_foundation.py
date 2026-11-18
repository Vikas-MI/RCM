"""Phase 1 foundation — empty schema placeholder.

Revision ID: 20261112_0001
Revises:
Create Date: 2026-11-12

Tables for patients, encounters, payers, insurance, and eligibility
are added in Phase 3 once models are defined.
"""

from typing import Sequence, Union

revision: str = "20261112_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No tables yet — Phase 1 only wires Alembic + SQLAlchemy.
    pass


def downgrade() -> None:
    pass

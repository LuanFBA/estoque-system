"""ajustar geração de data

Revision ID: 60914b7a199c
Revises: dfddbab1cdd5
Create Date: 2025-12-21 22:26:29.186226

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "60914b7a199c"
down_revision: Union[str, Sequence[str], None] = "dfddbab1cdd5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

"""Add toxic tag

Revision ID: f32841395145
Revises: 67a256363095
Create Date: 2025-03-13 15:55:15.404269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from core.utils import current_utc_time

# revision identifiers, used by Alembic.
revision: str = 'f32841395145'
down_revision: Union[str, None] = '67a256363095'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Inserting system defined tags ###
    connection = op.get_bind()
    connection.execute(
        sa.text("""
                    INSERT INTO tag (status, create_time, update_time, type, name, description)
                    VALUES
                        (1, :now, :now, 'SYSTEM_DEFINED', 'TOXIC', 'The toxic content that is harmful, abusive, or offensive, including hate speech, harassment, and threats')
                """),
        {"now": current_utc_time()}
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### Deleting system defined tags ###
    connection = op.get_bind()
    connection.execute(
        sa.text("""
                    DELETE FROM tag
                    WHERE type = 'SYSTEM_DEFINED' AND name = 'TOXIC'
                """)
    )
    # ### end Alembic commands ###

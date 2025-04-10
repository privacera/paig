"""Added response templates

Revision ID: d1774fab58b0
Revises: dd5bdf787fa1
Create Date: 2025-03-31 16:29:08.541273

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from core.utils import current_utc_time

# revision identifiers, used by Alembic.
revision: str = 'd1774fab58b0'
down_revision: Union[str, None] = 'dd5bdf787fa1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Insert predefined templates
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            INSERT INTO response_template (response, description, status, create_time, update_time)
            VALUES 
            (
                'I couldn''t respond to that input. Please try rephrasing or let me know how I can assist you differently.',
                'Standard response for unclear or ambiguous input',
                1,
                :now,
                :now
            ),
            (
                'I''m unable to share that message due to privacy settings. Let me know if I can help with anything else.',
                'Response for privacy-related content restrictions',
                1,
                :now,
                :now
            ),
            (
                'This topic isn''t relevant to our discussion. Please ask something else I can help with.',
                'Response for off-topic or irrelevant queries',
                1,
                :now,
                :now
            ),
            (
                'I''m unable to respond to that request due to content guidelines. Let me know if there''s anything else I can assist you with.',
                'Response for content that violates guidelines',
                1,
                :now,
                :now
            )
        """),
        {"now": current_utc_time()}
    )


def downgrade() -> None:
    # Delete the predefined templates
    op.execute(
        text("""
            DELETE FROM response_template 
            WHERE response IN (
                'I couldn''t respond to that input. Please try rephrasing or let me know how I can assist you differently.',
                'I''m unable to share that message due to privacy settings. Let me know if I can help with anything else.',
                'This topic isn''t relevant to our discussion. Please ask something else I can help with.',
                'I''m unable to respond to that request due to content guidelines. Let me know if there''s anything else I can assist you with.'
            )
        """)
    )

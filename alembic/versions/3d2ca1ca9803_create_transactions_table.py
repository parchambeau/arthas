"""create transactions table

Revision ID: 3d2ca1ca9803
Revises: 
Create Date: 2023-04-20 14:11:40.664545

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d2ca1ca9803'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'transactions',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('datetime', sa.DateTime, nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('currency_code', sa.String(10), nullable=False),
        sa.Column('amount', sa.Numeric, nullable=False),
        sa.Column('amount_usd', sa.Numeric, nullable=False)              
    )


def downgrade() -> None:
    op.drop_table('transactions')

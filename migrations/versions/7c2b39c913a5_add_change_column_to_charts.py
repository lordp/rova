"""Add change column to Charts

Revision ID: 7c2b39c913a5
Revises: 10523eeaf3ff
Create Date: 2020-07-03 11:50:17.261748

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c2b39c913a5'
down_revision = '10523eeaf3ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('charts', sa.Column('change', sa.Integer(), nullable=True))
    op.create_index('week_year', 'charts', ['year', 'week'], unique=False)
    op.drop_index('ix_week_year', table_name='charts')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_week_year', 'charts', ['year', 'week'], unique=False)
    op.drop_index('week_year', table_name='charts')
    op.drop_column('charts', 'change')
    # ### end Alembic commands ###

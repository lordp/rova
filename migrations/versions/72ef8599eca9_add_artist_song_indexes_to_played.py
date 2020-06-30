"""Add artist/song indexes to Played

Revision ID: 72ef8599eca9
Revises: 99767de51fa2
Create Date: 2020-06-29 19:34:21.414840

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72ef8599eca9'
down_revision = '99767de51fa2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_played_artist_id'), 'played', ['artist_id'], unique=False)
    op.create_index(op.f('ix_played_song_id'), 'played', ['song_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_played_song_id'), table_name='played')
    op.drop_index(op.f('ix_played_artist_id'), table_name='played')
    # ### end Alembic commands ###

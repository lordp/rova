"""Add indexes to Played/Artist/Song

Revision ID: 99767de51fa2
Revises: 4c99cf37120e
Create Date: 2020-06-29 19:28:32.911665

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '99767de51fa2'
down_revision = '4c99cf37120e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_artist_slug', table_name='played_old')
    op.drop_index('idx_song_slug', table_name='played_old')
    op.drop_table('played_old')
    op.create_index(op.f('ix_artists_slug'), 'artists', ['slug'], unique=False)
    op.create_index(op.f('ix_played_played_time'), 'played', ['played_time'], unique=False)
    op.create_index(op.f('ix_songs_slug'), 'songs', ['slug'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_songs_slug'), table_name='songs')
    op.drop_index(op.f('ix_played_played_time'), table_name='played')
    op.drop_index(op.f('ix_artists_slug'), table_name='artists')
    op.create_table('played_old',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('station', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('artist', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('played_old _time', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('length', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('artist_slug', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('song_slug', sa.VARCHAR(length=255), server_default=sa.text("''::character varying"), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='played_old_pkey')
    )
    op.create_index('idx_song_slug', 'played_old', ['song_slug'], unique=False)
    op.create_index('idx_artist_slug', 'played_old', ['artist_slug'], unique=False)
    # ### end Alembic commands ###
"""create tables

Revision ID: d0048c27cf65
Revises: 
Create Date: 2022-10-24 13:22:50.948628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0048c27cf65'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(), nullable=False, unique=True),
        sa.Column('password', sa.Text, nullable=False),
        sa.Column('is_admin', sa.Boolean, nullable=False),
        sa.Column('last_login', sa.DateTime, nullable=False),
        sa.Column('session_token', sa.String(64), unique=True)
    )
    op.create_table(
        'person',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('nickname', sa.String(), nullable=True),
    )
    op.create_table(
        'directors',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('person_id', sa.Integer, nullable=False),
    )
    op.create_table(
        'actors',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('person_id', sa.Integer, nullable=False),
    )
    op.create_table(
        'movies',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('rating', sa.Integer, nullable=True),
        sa.Column('director_id', sa.Integer, nullable=False),
    )
    op.create_table(
        'movies_actors',
        sa.Column('movie_id', sa.ForeignKey('movies.id'), primary_key=True),
        sa.Column('actor_id', ForeignKey('actors.id'), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table('movies_actors')
    op.drop_table('movies')
    op.drop_table('actors')
    op.drop_table('directors')
    op.drop_table('person')

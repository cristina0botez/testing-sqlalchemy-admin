from sqlalchemy import Column, MetaData
from sqlalchemy.orm import mapper

from example import models


metadata = MetaData()

users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(50), nullable=False, unique=True),
    Column('password', Text, nullable=False),
    Column('is_admin', Boolean, nullable=False),
    Column('last_login', DateTime(timezone=True), nullable=False),
    Column('session_token', String(64), unique=True)
)

person = Table(
    'person',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), nullable=False),
    Column('nickname', String(50), nullable=True),
)

directors = Table(
    'directors',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('person_id', ForeignKey('person.id'), nullable=False),
)

actors = Table(
    'actors',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('person_id', ForeignKey('person.id'), nullable=False),
)

movies = Table(
    'movies',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String(100), nullable=False),
    Column('rating', Integer, nullable=True),
    Column('director_id', ForeignKey('actors.id'), nullable=False),
)

movies_actors = Table(
    'movies_actors',
    metadata,
    Column('movie_id', ForeignKey('movies.id'), primary_key=True),
    Column('actor_id', ForeignKey('actors.id'), primary_key=True),
)


def map_models_to_tables():
    user_mapper = mapper(models.User, users)
    person_mapper = mapper(models.person, person)
    director_mapper = mapper(models.director, directors)
    actor_mapper = mapper(models.actor, actors)
    movie_mapper = mapper(models.movie, movies)

from sqlalchemy import Column, Integer, String, create_engine, Table, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy_utils.types.password import PasswordType


Base = declarative_base()
engine = create_engine(
    'sqlite:///example.db',
    connect_args={'check_same_thread': False},
)
Session = sessionmaker(engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(PasswordType(schemes=['pbkdf2_sha512']))
    is_admin = Column(Boolean, nullable=False, default=False)
    last_login = Column(DateTime)
    session_token = Column(String, unique=True)


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    nickname = Column(String)


class Director(Base):
    __tablename__ = 'directors'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    movies = relationship('Movie', back_populates='director')


movies_actors = Table(
    'movies_actors',
    Base.metadata,
    Column('movie_id', ForeignKey('movies.id'), primary_key=True),
    Column('actor_id', ForeignKey('actors.id'), primary_key=True),
)


class Actor(Base):
    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    movies = relationship('Movie', secondary=movies_actors, back_populates='actors')


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    rating = Column(Integer, nullable=True)
    director_id = Column(Integer, ForeignKey('directors.id'), nullable=False)
    director = relationship('Director', back_populates='movies')
    actors = relationship('Actor', secondary=movies_actors, back_populates='movies')


Base.metadata.create_all(engine)

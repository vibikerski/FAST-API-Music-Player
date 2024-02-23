from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from .database import Base

association_table = Table(
    'association', Base.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id')),
    Column('track_id', Integer, ForeignKey('tracks.id'))
)

class Author(Base):
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    alias = Column(String, unique=True)
    
    tracks = relationship("Track", back_populates="parent")


class Track(Base):
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String)
    alias = Column(String, unique=True)
    
    description = Column(String)
    
    track_url = Column(String, unique=True)
    image_url = Column(String)
    
    author_id = Column(Integer, ForeignKey("authors.id"))
    
    parent = relationship("Author",back_populates="tracks")
    playlists = relationship("Playlist", secondary=association_table, back_populates="tracks")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    rights = Column(String, default="user")
    salt = Column(String)
    
    bio = Column(String, default="")
    
    playlists = relationship("Playlist", back_populates="creator")

class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    alias = Column(String, unique=True, index=True)
    description = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"))

    creator = relationship("User", back_populates="playlists")
    tracks = relationship("Track", secondary=association_table, back_populates="playlists")
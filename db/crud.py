from sqlalchemy.orm import Session, joinedload
from . import models, schemas
from passlib.context import CryptContext

import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# USER

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    salt = user.salt
    return user if verify_password(password, user.hashed_password, salt) else False


def create_user(db: Session, username: str, password: str, rights: str = "user"):
    salt = secrets.token_bytes(16)
    
    hashed_password = get_password_hash(password + salt)
    db_user = models.User(username=username, hashed_password=hashed_password, salt=salt, rights=rights)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password, salt):
    return pwd_context.verify(plain_password + salt, hashed_password)


# AUTHOR


def get_author(db: Session, author_id: int | None = None, author_alias: str | None = None):
    if author_id:
        return db.query(models.Author).filter(models.Author.id == author_id).first()
    if author_alias:
        return db.query(models.Author).filter(models.Author.alias == author_alias).first()


def get_authors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Author).offset(skip).limit(limit).all()


def create_author(db: Session, author: schemas.AuthorCreate):
    db_author = models.Author(**author.model_dump())

    db.add(db_author)
    db.commit()
    db.refresh(db_author)

    return db_author

def delete_author_with_tracks(db: Session, author_id: int | None = None, author_alias: str | None = None):
    author = db.query(models.Author)
    if author_id:
        author = author.filter(models.Author.id == author_id).first()
    else:
        author = author.filter(models.Author.alias == author_alias).first()

    if author:
        tracks = db.query(models.Track).filter(models.Track.author_id == author_id).all()
        for track in tracks:
            db.delete(track)
        
        db.delete(author)
        db.commit()
        return True
    return False


# TRACK


def get_track(db: Session, track_id:int | None = None, track_alias: str | None = None):
    if track_id:
        return db.query(models.Track).filter(models.Track.id == track_id).first()
    if track_alias:
        return db.query(models.Track).filter(models.Track.alias == track_alias).first()


def get_tracks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Track).offset(skip).limit(limit).all()


def get_tracks_by_an_author(
    db: Session,
    author_id: int | None = None,
    author_alias: str | None = None,
    skip: int = 0,
    limit: int = 100
):
    if author_id is None:
        author_id = get_author(db, author_alias=author_alias)
    return db.query(models.Track).filter(models.Track.author_id == author_id).offset(skip).limit(limit).all()


def create_track(db: Session, track: schemas.TrackCreate, author_id: int| None = None, author_alias: str | None = None):
    if author_id is None:
        author_id = get_author(db, author_alias=author_alias).id

    db_track = models.Track(**track.model_dump(), author_id = author_id)

    db.add(db_track)
    db.commit()
    db.refresh(db_track)

    return db_track

def delete_track(db: Session, track_id: int | None = None, track_alias: int | None = None):
    track = db.query(models.Track)
    if track_id:
        track = track.filter(models.Track.id == track_id).first()
    else:
        track = track.filter(models.Track.alias == track_alias).first()

    if track:
        db.delete(track)
        db.commit()
        return True
    return False


# PLAYLIST


def create_playlist(
    db: Session,
    title: str,
    alias: str,
    description: str,
    creator_id: int | None = None,
    creator_username: str | None = None
):
    if creator_id is None:
        creator_id = get_user(db, creator_username).id
    
    playlist_exists = bool(db.query(models.Playlist).filter(models.Playlist.alias == alias).first())
    if playlist_exists:
        return None
    
    
    db_playlist = models.Playlist(title=title, alias=alias, creator_id=creator_id, description=description)
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist


def add_track_to_playlist(
    db: Session,
    playlist_id: int | None = None,
    playlist_alias: str | None = None,
    track_id: int | None = None,
    track_alias: str | None = None
):
    playlist = ''
    track = ''
    if playlist_id:
        playlist = db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()
    else:
        playlist = db.query(models.Playlist).filter(models.Playlist.alias == playlist_alias).first()
    
    if track_id:
        track = db.query(models.Track).filter(models.Track.id == track_id).first()
    else:
        track = db.query(models.Track).filter(models.Track.alias == track_alias).first()


    if not playlist or not track:
        return None

    playlist.tracks.append(track)
    db.commit()
    db.refresh(playlist)
    return playlist


def get_playlist(db: Session, playlist_id: int | None = None, playlist_alias: str | None = None):
    query = db.query(models.Playlist).options(joinedload(models.Playlist.tracks))

    if playlist_id:
        return query.filter(models.Playlist.id == playlist_id).first()
    return query.filter(models.Playlist.alias == playlist_alias).first()


def get_playlists(db: Session):
    return db.query(models.Playlist).options(joinedload(models.Playlist.tracks)).all()


def delete_playlist(db: Session, playlist_id: int | None = None, playlist_alias: str | None = None):
    playlist = db.query(models.Playlist)
    if playlist_id:
        playlist = playlist.filter(models.Playlist.id == playlist_id).first()
    else:
        playlist = playlist.filter(models.Playlist.alias == playlist_alias).first()

    if playlist:
        db.delete(playlist)
        db.commit()
        return True
    return False

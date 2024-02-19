from fastapi import Path, Depends, HTTPException, APIRouter
from fastapi.templating import Jinja2Templates

from starlette.requests import Request
from typing import Annotated

from sqlalchemy.orm import Session
from db import crud, schemas

from handle_db import *

templates = Jinja2Templates(directory="templates")
tracks_router = APIRouter()


def change_track_data(tracks, db):
    for track in tracks:
        track.track_url = f"audio/{track.track_url}"
        track.image_url = f"img/{track.image_url}"
        track.author = crud.get_author(db, track.author_id).name
    return tracks

# GET PAGES WITH AUTHORS


@tracks_router.get("/", response_model=list[schemas.Author])
async def read_authors(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    authors = crud.get_authors(db, skip=skip, limit=limit)
    return templates.TemplateResponse(
        "authors.html",
        {"request": request, "authors": authors}
    )


@tracks_router.get("/authors/{author_alias}", response_model=schemas.Author)
async def read_author(
        request: Request,
        author_alias: Annotated[str, Path(min_length=3, max_length=50)],
        db: Session = Depends(get_db)
):
    db_author = crud.get_author(db, author_alias=author_alias)

    if db_author is None:
        raise HTTPException(404, "Author not found")

    tracks = change_track_data(
        crud.get_tracks_by_an_author(db, db.author.id),
        db
    )
    return templates.TemplateResponse(
        "songsbyauthors.html",
        {"request": request, "author_name": db_author.name, "songs": tracks}
    )

# GET PAGES WITH TRACKS


@tracks_router.get('/tracks/all', response_model=list[schemas.Track])
async def read_tracks(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    tracks = change_track_data(crud.get_tracks(db, skip=skip, limit=limit), db)
    return templates.TemplateResponse(
        "songs.html",
        {"request": request, "songs": tracks}
    )


@tracks_router.get("/tracks/{track_alias}")
async def display_song(
        request: Request,
        track_alias: Annotated[str, Path(min_length=3, max_length=50)],
        db: Session = Depends(get_db)
):
    track = change_track_data(
        [crud.get_track(db, track_alias=track_alias)],
        db
    )[0]
    return templates.TemplateResponse(
        "song.html",
        {"request": request, "track": track}
    )

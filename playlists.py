from fastapi import Depends, HTTPException, APIRouter
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from starlette.requests import Request
from db import crud, models, schemas

from handle_db import *
from security import get_current_user
from display_tracks import change_track_data

templates = Jinja2Templates(directory="templates")

playlist_router = APIRouter()


@playlist_router.post("/playlists/", response_model=schemas.Playlist)
async def create_playlist(
    playlist: schemas.PlaylistCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if playlist := crud.create_playlist(
        db,
        playlist.title,
        playlist.alias,
        playlist.description,
        current_user.id
    ):
        return playlist

    raise HTTPException(400, "Playlist with this alias already exists")


@playlist_router.post("/playlists/{playlist_alias}/tracks/{track_alias}")
async def add_track_to_playlist(
    playlist_alias: str,
    track_alias: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    playlist = crud.get_playlist(db, playlist_alias=playlist_alias)

    if not playlist:
        raise HTTPException(404, "Playlist not found")

    if current_user.rights != "admin" and current_user.id != playlist.creator_id:
        raise HTTPException(403, "You are not allowed to modify this playlist")

    if added_track := crud.add_track_to_playlist(
        db,
        playlist_alias=playlist_alias,
        track_alias=track_alias
    ):
        return added_track

    raise HTTPException(404, "Track not found")


@playlist_router.get("/playlists/all")
async def get_playlists(request: Request, db: Session = Depends(get_db)):
    playlists = crud.get_playlists(db)

    playlists_data = []
    for playlist in playlists:
        playlist_info = {
            "title": playlist.title,
            "alias": playlist.alias,
            "creator": playlist.creator.username,
            "tracks": playlist.tracks[:5] if playlist.tracks else [],
            "description": playlist.description
        }
        playlists_data.append(playlist_info)

    return templates.TemplateResponse(
        "all_playlists.html",
        {"request": request, "playlists": playlists_data}
    )


@playlist_router.get("/playlists/{playlist_alias}")
async def get_playlist(
    request: Request,
    playlist_alias: str,
    db: Session = Depends(get_db)
):
    playlist = crud.get_playlist(db, playlist_alias=playlist_alias)
    playlist.tracks = change_track_data(playlist.tracks, db)
    return templates.TemplateResponse(
        "playlist.html",
        {"request": request,
         "playlist": playlist,
         "creator": playlist.creator.username}
    )

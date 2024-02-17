from fastapi import Depends, HTTPException, APIRouter, Path
from typing import Annotated
from sqlalchemy.orm import Session
from db import models, crud

from handle_db import *
from security import get_current_user, check_admin_rights

deletion_router = APIRouter()

def handle_deletion(crud_func, db: Session, identifier: str, entity_name: str):
    if not crud_func(db, None, identifier):
        raise HTTPException(404, f"{entity_name} not found")
    return "Success"

@deletion_router.delete("/music/tracks/{track_alias}")
async def delete_track(
    track_alias: Annotated[str, Path(min_length=3, max_length=50)],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    check_admin_rights(current_user)
    return handle_deletion(crud.delete_track, db, track_alias, "Track")

@deletion_router.delete("/music/playlists/{playlist_alias}")
async def delete_playlist(
    playlist_alias: Annotated[str, Path(min_length=3, max_length=50)],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    playlist = crud.get_playlist(db, playlist_alias=playlist_alias)
    if not playlist:
        raise HTTPException(404, "Playlist not found")

    creator = playlist.creator_id
    if current_user.rights != "admin" and current_user.id != creator:
        raise HTTPException(403, "You do not have rights to delete this playlist")

    crud.delete_playlist(db, None, playlist_alias)
    return "Success"


@deletion_router.delete("/music/authors/{author_alias}")
async def delete_author(
    author_alias: Annotated[str, Path(min_length=3, max_length=50)],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    check_admin_rights(current_user)
    return handle_deletion(crud.delete_author_with_tracks, db, author_alias, "Author")

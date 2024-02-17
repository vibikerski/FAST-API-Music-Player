from fastapi import Path, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from db import crud, models, schemas
from typing import Annotated

from security import get_current_user, check_admin_rights
from handle_db import get_db

post_router = APIRouter()

@post_router.post("/music/authors/", response_model=schemas.Author)
async def create_author(
    author: schemas.AuthorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    check_admin_rights(current_user)
    return crud.create_author(db=db, author=author)

@post_router.post("/music/authors/{author_alias}/tracks/", response_model=schemas.Track)
async def create_track(
    author_alias: Annotated[str, Path(min_length=3, max_length=50)],
    track: schemas.TrackCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    check_admin_rights(current_user)
    allowed_extensions = ('mp3', 'ogg', 'wav', 'm4a')
    file_extension = track.track_url.split(".")[-1]
    if file_extension not in allowed_extensions:
        raise HTTPException(400, "The file extension is not allowed")
        
    return crud.create_track(db=db, track=track, author_alias=author_alias)
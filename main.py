from app_initialize import app

from handle_db import *
from security import *
from handle_post_request import post_router
from display_tracks import tracks_router
from playlists import playlist_router
from deletion import deletion_router
from account_management import account_router

# imports for re-creating the db
from db import models
from db.database import engine

app.include_router(post_router)
app.include_router(security_router)
app.include_router(tracks_router)
app.include_router(playlist_router)
app.include_router(deletion_router)
app.include_router(account_router)

# run when models are changed
# models.Base.metadata.create_all(bind=engine)

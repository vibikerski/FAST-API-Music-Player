from fastapi import Depends, APIRouter, Form, Header
from fastapi.responses import RedirectResponse

from starlette.requests import Request
from typing import Annotated

from sqlalchemy.orm import Session
from db import models, crud

from handle_db import *
from security import create_user, get_current_user
from app_initialize import templates

account_router = APIRouter()

@account_router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {
        "request": request,
    })

@account_router.post("/register")
async def register_user(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(get_db)
):
    user = {
        'username': username,
        'password': password
    }
    create_user(user, db)
    return RedirectResponse("/auth", 303)


@account_router.get("/account")
async def get_account(
    request: Request,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
    user: models.User = Depends(get_current_user),
):
    if authorization is None:
        if token := request.cookies.get("access_token"):
            authorization = f"Bearer {token}"

    account = crud.get_user(db, username=user.username)
    context = {
        'request': request,
        'username': account.username,
        'bio': account.bio,
        'playlists': account.playlists
    }
    return templates.TemplateResponse(
        "my_account.html",
        context
    )
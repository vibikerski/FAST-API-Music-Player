from fastapi import Depends, APIRouter, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from starlette.requests import Request
from typing import Annotated

from sqlalchemy.orm import Session

from handle_db import *
from security import create_user

register_router = APIRouter()

templates = Jinja2Templates(directory="templates")

@register_router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@register_router.post("/register")
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
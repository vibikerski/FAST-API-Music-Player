from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.requests import Request

from handle_db import get_db
from sqlalchemy.orm import Session
from db import crud, schemas
from secret_key import SECRET_KEY # excluded in gitignore
from app_initialize import templates

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

security_router = APIRouter()

def token_create(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            raise HTTPException(status_code=401, detail="Not authenticated")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(401, detail="Could not validate credentials")
        user = crud.get_user(db, username=username)
        if user is None:
            raise HTTPException(401, detail="Could not validate credentials")
        return user
    except JWTError as e:
        raise HTTPException(401, detail="Could not validate credentials") from e

@security_router.post("/token")
async def token_get(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = token_create(data={"sub": user.username},)

    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user(db, user['username']):
        raise HTTPException(400, "Such username already exists")

    return crud.create_user(db, user['username'], user['password'])

@security_router.get("/auth")
async def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {'request': request})

def check_admin_rights(current_user):
    if current_user.rights != "admin":
        raise HTTPException(403, "You do not have rights for this action.")

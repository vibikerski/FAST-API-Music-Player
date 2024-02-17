from pydantic import BaseModel

class TrackBase(BaseModel):
    title: str
    alias: str
    description: str | None = None
    track_url: str
    image_url: str | None = None


class TrackCreate(TrackBase):
    pass


class Track(TrackBase):
    id: int
    author_id: int
    
    class Config:
        from_attributed = True


class AuthorBase(BaseModel):
    name: str
    alias: str


class AuthorCreate(AuthorBase):
    pass


class Author(AuthorBase):
    id: int
    tracks: list[Track] = []
    
    class Config:
        from_attributed = True


class UserBase(BaseModel):
    username: str


class UserDB(UserBase):
    hashed_password: str
    salt: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    rights: str = "user"
    
    class Config:
        from_attributed = True


class PlaylistBase(BaseModel):
    title: str
    alias: str
    description: str


class PlaylistCreate(PlaylistBase):
    pass


class Playlist(PlaylistBase):
    id: int
    tracks: list[TrackBase] = []

    class Config:
        from_attributed = True
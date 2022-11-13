from pydantic import BaseModel, HttpUrl


class PhotoSizes(BaseModel):
    url: HttpUrl
    type: str


class Photo(BaseModel):
    date: int
    sizes: list[PhotoSizes]


class VideoCover(BaseModel):
    url: HttpUrl


class Video(BaseModel):
    title: str
    duration: int
    image: list[VideoCover]
    date: int
    player: HttpUrl | None = None


class Attachment(BaseModel):
    type: str
    photo: Photo | None = None
    video: Video | None = None


class Post(BaseModel):
    id: int
    from_id: int
    date: int
    text: str
    attachments: list[Attachment]

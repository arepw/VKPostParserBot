from pydantic import BaseModel, HttpUrl, Field


class PhotoSizes(BaseModel):
    url: HttpUrl
    type: str


class Photo(BaseModel):
    date: int
    sizes: list[PhotoSizes]


class Audio(BaseModel):
    id: int
    owner_id: int
    artist: str
    title: str
    duration: int
    url: HttpUrl


class AudiosList(BaseModel):
    items: list[Audio] = Field(..., alias='response')


class VideoCover(BaseModel):
    url: HttpUrl


class VideoFiles(BaseModel):
    mp4_144: HttpUrl | None = None
    mp4_240: HttpUrl | None = None
    mp4_360: HttpUrl | None = None
    mp4_480: HttpUrl | None = None


class Video(BaseModel):
    title: str
    duration: int
    files: VideoFiles | None = None
    image: list[VideoCover]
    date: int
    player: HttpUrl | None = None
    platform: str | None = None
    id: int
    owner_id: int


class VideosList(BaseModel):
    count: int
    items: list[Video]


class Attachment(BaseModel):
    type: str
    photo: Photo | None = None
    video: Video | None = None
    audio: Audio | None = None


class Post(BaseModel):
    id: int
    from_id: int
    date: int
    text: str
    attachments: list[Attachment]

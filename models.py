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
    mp4_720: HttpUrl | None = None

    def preferred_video_file(self, video_duration: int) -> str:
        """
        Iterates through VideoFiles attributes to find the most suitable video quality
        :return: str video download url.
        """
        files = [self.mp4_480, self.mp4_360, self.mp4_240, self.mp4_144]
        durations = [90, 120, 180, 240]
        for item in range(len(files)):
            if files[item] is not None and video_duration < durations[item]:
                return files[item]
        raise AttributeError


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
    attachments: list[Attachment] | None = None

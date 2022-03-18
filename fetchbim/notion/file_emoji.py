import datetime

from typing import Optional
from pydantic import BaseModel, HttpUrl


class FileURL(BaseModel):
    url: str
    expiry_time: Optional[datetime.datetime]


class ExternalFile(BaseModel):
    type: str = "external"
    external: FileURL


class HostedFile(BaseModel):
    type: str = "file"
    file: FileURL


class FileObject(BaseModel):
    type: ExternalFile | HostedFile

    class Config:
        arbitrary_types_allowed = True


class EmojiObject(BaseModel):
    type: str = "emoji"
    emoji: str

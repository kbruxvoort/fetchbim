import datetime

from typing import Optional
from pydantic import BaseModel, HttpUrl


class FileURL(BaseModel):
    url: str
    expiry_time: Optional[datetime.datetime]


class ExternalFile(BaseModel):
    type: str = "external"
    external: FileURL

    def get_value(self):
        return self.external.url


class HostedFile(BaseModel):
    type: str = "file"
    file: FileURL

    def get_value(self):
        return self.file.url


class FileObject(BaseModel):
    type: ExternalFile | HostedFile

    class Config:
        arbitrary_types_allowed = True


class EmojiObject(BaseModel):
    type: str = "emoji"
    emoji: str

import datetime

from enum import Enum
from typing import Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, HttpUrl
from .rich_text import RichText, Color
from .user import User
from .file_emoji import HostedFile, ExternalFile


class PropertyType(str, Enum):
    Title = "title"
    rich_text = "rich_text"
    number = "number"
    select = "select"
    multi_select = "multi_select"
    date = "date"
    people = "people"
    files = "files"
    checkbox = "checkbox"
    url = "url"
    email = "email"
    phone_number = "phone_number"
    formula = "formula"
    relation = "relation"
    rollup = "rollup"
    created_time = "created_time"
    created_by = "created_by"
    last_edited_time = "last_edited_time"
    last_edited_by = "last_edited_by"

    def __str__(self):
        return self.value


class Date(BaseModel):
    start: datetime.date | datetime.datetime
    end: Optional[datetime.date | datetime.datetime] = None
    time_zone: Optional[str] = None


class Property(BaseModel):
    id: str
    type: PropertyType
    name: Optional[str]

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True


class Select(BaseModel):
    id: UUID
    name: str
    color: Color

    class Config:
        use_enum_values = True


class TitleProperty(Property):
    title: list[RichText]

    def get_value(self):
        return self.title[0].plain_text


class CheckboxProperty(Property):
    checkbox: bool


class MultiSelectProperty(Property):
    multi_select: list[Select]


class SelectProperty(Property):
    select: Select


class PersonProperty(Property):
    person: list[User]


class EmailProperty(Property):
    email: str


class PhoneProperty(Property):
    phone_number: str


class URLProperty(Property):
    url: HttpUrl | str


class FileProperty(Property):
    files: list[HostedFile | ExternalFile]


class NumberProperty(Property):
    number: float | int


class DateProperty(Property):
    date: Date


# class RelationProperty(Property):
#     relation: list[dict]

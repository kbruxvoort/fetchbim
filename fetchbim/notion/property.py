import datetime

from enum import Enum
from typing import Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, HttpUrl
from .rich_text import RichText, Color
from .user import User
from .file_emoji import HostedFile, ExternalFile


class RollupType(str, Enum):
    count_all = "count_all"
    count_values = "count_values"
    count_unique_values = "count_unique_values"
    count_empty = "count_empty"
    count_not_empty = "count_not_empty"
    percent_empty = "percent_empty"
    percent_not_empty = "percent_not_empty"
    _sum = "sum"
    _average = "average"
    _median = "median"
    _min = "min"
    _max = "max"
    _range = "range"
    show_original = "show_original"

    def __str__(self):
        return self.value


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


class Formula(BaseModel):
    type: str = "formula"
    string: str


class Rollup(BaseModel):
    pass


class Property(BaseModel):
    id: str
    type: PropertyType
    # name: Optional[str]

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
        return "".join([text.plain_text for text in self.title])


class RichTextProperty(Property):
    rich_text: list[RichText]

    def get_value(self):
        return "".join([text.plain_text for text in self.rich_text])


class CheckboxProperty(Property):
    checkbox: bool

    def get_value(self):
        return self.checkbox


class MultiSelectProperty(Property):
    multi_select: list[Select]

    def get_value(self):
        return [select.name for select in self.multi_select]


class SelectProperty(Property):
    select: Select

    def get_value(self):
        return self.select.name


class PersonProperty(Property):
    people: list[User]

    def get_value(self):
        return [user.id for user in self.people]


class EmailProperty(Property):
    email: str

    def get_value(self):
        return self.email


class PhoneProperty(Property):
    phone_number: str

    def get_value(self):
        return self.phone_number


class URLProperty(Property):
    url: HttpUrl | str

    def get_value(self):
        return self.url


class FileProperty(Property):
    files: list[HostedFile | ExternalFile]

    def get_value(self):
        return [_file.get_value() for _file in self.files]


class NumberProperty(Property):
    number: float | int

    def get_value(self):
        return self.number


class DateProperty(Property):
    date: Date

    def get_value(self):
        return self.date.start


class FormulaProperty(Property):
    formula: Formula

    def get_value(self):
        return self.formula.string


class RelationProperty(Property):
    relation: list[Dict[str, UUID]]

    def get_value(self):
        return [_id["id"] for _id in self.relation]


class RollupProperty(Property):
    relation_property_name: str
    relation_property_id: str
    rollup_property_name: str
    rollup_property_id: str
    function: RollupType

    class Config:
        use_enum_values = True

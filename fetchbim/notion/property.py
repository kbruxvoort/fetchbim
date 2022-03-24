from __future__ import annotations
import datetime

from enum import Enum
from pydoc import plain
from typing import Dict, Any, Optional, Literal
from uuid import UUID

from pydantic import BaseModel, HttpUrl
from .rich_text import Annotation, RichText, Color, RichTextType, Text
from .user import User
from .file_emoji import HostedFile, ExternalFile
from fetchbim.notion import rich_text


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
    show_unique = "show_unique"
    latest_date = "latest_date"
    earliest_date = "earliest_date"
    date_range = "date_range"

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

    def get_value(self):
        if self.start:
            return self.start


class FormulaString(BaseModel):
    type: Literal["string"] = "string"
    string: Optional[str] = None

    def get_value(self):
        if self.string:
            return self.string


class Relation(BaseModel):
    id: UUID

    def get_value(self):
        return self.id


class Select(BaseModel):
    id: Optional[UUID] = None
    name: str
    color: Optional[Color] = Color.default

    class Config:
        use_enum_values = True

    def get_value(self):
        if self.name:
            return self.name


class Property(BaseModel):
    id: Optional[str] = None
    type: PropertyType

    def get_value(self):
        return self.type


class TitleProperty(Property):
    type: Literal["title"] = "title"
    title: Optional[list[RichText]]

    def get_value(self):
        if self.title:
            return "".join([text.plain_text for text in self.title])

    def to_notion(self):
        return self.dict(include={"title": {0: {"text": {"content"}}}})

    @classmethod
    def from_value(cls, value):
        return cls(
            title=[
                RichText(
                    plain_text=value,
                    annotations=Annotation(),
                    type=RichTextType.text,
                    text=Text(content=value),
                )
            ]
        )


class RichTextProperty(Property):
    type: Literal["rich_text"] = "rich_text"
    rich_text: Optional[list[RichText]] = []

    def get_value(self):
        if self.rich_text:
            return "".join([text_item.plain_text for text_item in self.rich_text])

    def to_notion(self):
        return self.dict(include={"rich_text": {0: {"text": {"content"}}}})

    @classmethod
    def from_value(cls, value):
        return cls(
            rich_text=[
                RichText(
                    plain_text=value,
                    annotations=Annotation(),
                    type=RichTextType.text,
                    text=Text(content=value),
                )
            ]
        )

    class Config:
        use_enum_values = True


class CheckboxProperty(Property):
    type: Literal["checkbox"] = "checkbox"
    checkbox: bool

    def get_value(self):
        return self.checkbox

    def to_notion(self):
        return self.dict(include={"checkbox"})


class BooleanProperty(Property):
    type: Literal["boolean"] = "boolean"
    boolean: bool

    def get_value(self):
        return self.boolean

    def to_notion(self):
        return self.dict(include={"boolean"})


class MultiSelectProperty(Property):
    type: Literal["multi_select"] = "multi_select"
    multi_select: Optional[list[Select]]

    def get_value(self):
        if self.multi_select:
            return [select.get_value() for select in self.multi_select]


class SelectProperty(Property):
    type: Literal["select"] = "select"
    select: Optional[Select]

    def get_value(self):
        if self.select:
            return self.select.get_value()

    def to_notion(self):
        return self.dict(include={"select": {"name"}})

    @classmethod
    def from_value(cls, value):
        return cls(select=Select(name=value))


class PersonProperty(Property):
    type: Literal["people"] = "people"
    people: Optional[list[User]]

    def get_value(self):
        if self.people:
            return [user.get_value() for user in self.people]


class EmailProperty(Property):
    type: Literal["email"] = "email"
    email: Optional[str]

    def get_value(self):
        if self.email:
            return self.email


class PhoneProperty(Property):
    type: Literal["phone_number"] = "phone_number"
    phone_number: Optional[str]

    def get_value(self):
        return self.phone_number


class URLProperty(Property):
    type: Literal["url"] = "url"
    url: Optional[HttpUrl | str]

    def get_value(self):
        if self.url:
            return self.url


class FileProperty(Property):
    type: Literal["files"] = "files"
    files: Optional[list[HostedFile | ExternalFile]]

    def get_value(self):
        if self.files:
            return [_file.get_value() for _file in self.files]


class NumberProperty(Property):
    type: Literal["number"] = "number"
    number: Optional[float | int]

    def get_value(self):
        if self.number:
            return self.number


class DateProperty(Property):
    type: Literal["date"] = "date"
    date: Optional[Date]

    def get_value(self):
        if self.date:
            return self.date.start


class FormulaProperty(Property):
    type: Literal["formula"] = "formula"
    formula: Optional[
        FormulaString
        | NumberProperty
        | DateProperty
        | CheckboxProperty
        | BooleanProperty
    ]

    def get_value(self):
        if self.formula:
            return self.formula.get_value()


class RelationProperty(Property):
    type: Literal["relation"] = "relation"
    relation: Optional[list[Relation]]

    def get_value(self):
        if self.relation:
            return [_id.get_value() for _id in self.relation]


class ArrayProperty(BaseModel):
    type: Literal["array"]
    function: RollupType
    # array: Any
    array: Optional[
        list[
            TitleProperty
            | CheckboxProperty
            | PersonProperty
            | EmailProperty
            | MultiSelectProperty
            | SelectProperty
            | PhoneProperty
            | URLProperty
            | FileProperty
            | DateProperty
            | NumberProperty
            | FormulaProperty
            | RelationProperty
            | RichTextProperty
        ]
    ] = []

    class Config:
        use_enum_values = True

    def get_value(self):
        if self.array:
            return [prop.get_value() for prop in self.array]


class RollupProperty(Property):
    type: Literal["rollup"]
    rollup: (
        Optional[
            ArrayProperty
            | TitleProperty
            | CheckboxProperty
            | PersonProperty
            | EmailProperty
            | MultiSelectProperty
            | SelectProperty
            | PhoneProperty
            | URLProperty
            | FileProperty
            | DateProperty
            | NumberProperty
            | FormulaProperty
            | RelationProperty
            | RichTextProperty
        ]
    )

    def get_value(self):
        if self.rollup:
            return self.rollup.get_value()


class CreatedTimeProperty(Property):
    type: Literal["created_time"]
    created_time: datetime.datetime

    def get_value(self):
        return self.created_time


class EditedTimeProperty(Property):
    type: Literal["last_edited_time"]
    last_edited_time: datetime.datetime

    def get_value(self):
        return self.last_edited_time


class CreatedByProperty(Property):
    type: Literal["created_by"]
    created_by: User

    def get_value(self):
        return self.created_by.get_value()


class EditedByProperty(Property):
    type: Literal["last_edited_by"]
    last_edited_by: User

    def get_value(self):
        return self.last_edited_by.get_value()

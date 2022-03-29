from typing import Optional
from enum import Enum

from pydantic import BaseModel, HttpUrl


class RichTextType(str, Enum):
    text = "text"
    mention = "mention"
    equation = "equation"

    def __str__(self):
        return self.value


class Color(str, Enum):
    default = "default"
    gray = "gray"
    brown = "brown"
    orange = "orange"
    yellow = "yellow"
    green = "green"
    blue = "blue"
    purple = "purple"
    pink = "pink"
    red = "red"
    gray_background = "gray_background"
    brown_background = "brown_background"
    orange_background = "orange_background"
    yellow_background = "yellow_background"
    green_background = "green_background"
    blue_background = "blue_background"
    purple_background = "purple_background"
    pink_background = "pink_background"
    red_background = "red_background"

    def __str__(self):
        return self.value


class MentionType(str, Enum):
    user = "user"
    page = "page"
    database = "database"
    date = "date"
    link_preview = "link_preview"

    def __str__(self):
        return self.value


class Link(BaseModel):
    type: str = "url"
    url: Optional[HttpUrl] = None


class Text(BaseModel):
    content: Optional[str]
    link: Optional[Link] = None


class Mention(BaseModel):
    type: MentionType

    class Config:
        use_enum_values = True


class Equation(BaseModel):
    expression: str


class Annotation(BaseModel):
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: Color = Color.default

    class MyConfig:
        use_enum_values = True


class RichText(BaseModel):
    plain_text: Optional[str] = None
    href: Optional[str] = None
    annotations: Optional[Annotation] = None
    type: RichTextType
    text: Optional[Text]

    class Config:
        use_enum_values = True

from __future__ import annotations

import datetime

from typing import TYPE_CHECKING, Optional, Any, Dict
from uuid import UUID


from pydantic import BaseModel, HttpUrl, validator


from .user import User
from .file_emoji import ExternalFile, HostedFile, EmojiObject
from .parent import PageParent, WorkspaceParent, DatabaseParent
from .property import (
    Property,
    RelationProperty,
    TitleProperty,
    CheckboxProperty,
    PersonProperty,
    EmailProperty,
    MultiSelectProperty,
    SelectProperty,
    PhoneProperty,
    URLProperty,
    FileProperty,
    DateProperty,
    NumberProperty,
    FormulaProperty,
    RelationProperty,
    RichTextProperty,
    RollupProperty,
    CreatedTimeProperty,
    CreatedByProperty,
    EditedTimeProperty,
    EditedByProperty,
)


class Page(BaseModel):
    object: str = "page"
    id: UUID | str
    created_time: datetime.datetime | str
    created_by: User
    last_edited_time: datetime.datetime | str
    last_edited_by: User
    archived: bool = False
    icon: Optional[HostedFile | ExternalFile | EmojiObject] = None
    cover: Optional[HostedFile | ExternalFile] = None
    properties: Dict[
        str,
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
        | RollupProperty
        | CreatedTimeProperty
        | CreatedByProperty
        | EditedTimeProperty
        | EditedByProperty
        # | Property,
    ]
    parent: DatabaseParent | PageParent | WorkspaceParent
    url: HttpUrl

    class Config:
        arbitrary_types_allowed = True

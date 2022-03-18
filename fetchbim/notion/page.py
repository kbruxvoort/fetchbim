from __future__ import annotations

import datetime

from typing import TYPE_CHECKING, Optional, Any, Union
from uuid import UUID


from pydantic import BaseModel, HttpUrl, validator


from .user import User
from .file_emoji import ExternalFile, HostedFile, EmojiObject
from .parent import PageParent, WorkspaceParent, DatabaseParent
from .property import (
    Property,
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
    NumberProperty
)

# User = ForwardRef("User")


class Page(BaseModel):
    object: str = "page"
    id: UUID | str
    created_time: datetime.datetime | str
    created_by: User
    last_edited_time: datetime.datetime | str
    last_edited_by: User
    archived: bool = False
    icon: Optional[HostedFile | ExternalFile | EmojiObject] = None
    # icon: Optional[FileObject] | Optional[EmojiObject] = None
    cover: Optional[HostedFile | ExternalFile] = None
    properties: Any
    # properties: Optional[list[Property]] = []
    parent: DatabaseParent | PageParent | WorkspaceParent
    url: HttpUrl

    @validator("properties", pre=True)
    def set_by_type(cls, values):
        dct = {}
        std_props = [
            "title",
            "rich_text",
        ]
        for k, v in values.items():

            v["name"] = k
            if v.get("type") == "title":
                # lst.append(TitleProperty(**v))
                dct[k] = TitleProperty(**v)
            elif v.get("type") == "checkbox":
                # lst.append(CheckboxProperty(**v))
                dct[k] = CheckboxProperty(**v)
            elif v.get("type") == "person":
                # lst.append(PersonProperty(**v))
                dct[k] = PersonProperty(**v)
            elif v.get("type") == "email":
                # lst.append(EmailProperty(**v))
                dct[k] = EmailProperty(**v)
            elif v.get("type") == "multi_select":
                # lst.append(MultiSelectProperty(**v))
                dct[k] = MultiSelectProperty(**v)
            elif v.get("type") == "select":
                # lst.append(SelectProperty(**v))
                dct[k] = SelectProperty(**v)
            elif v.get("type") == "phone_number":
                # lst.append(PhoneProperty(**v))
                dct[k] = PhoneProperty(**v)
            elif v.get("type") == "url":
                # lst.append(URLProperty(**v))
                dct[k] = URLProperty(**v)
            elif v.get("type") == "file":
                # lst.append(FileProperty(**v))
                dct[k] = FileProperty(**v)
            elif v.get("type") == "person":
                # lst.append(PersonProperty(**v))
                dct[k] = PersonProperty(**v)
            elif v.get("type") == "date":
                dct[k] = DateProperty(**v)
            elif v.get("type") == "number":
                dct[k] = NumberProperty(**v)
            else:
                # lst.append(Property(**v))
                dct[k] = Property(**v)
            #     lst.append(TitleProperty(**v))
            # elif v.get("type") == "relation":
            #     lst.append(RelationProperty(**v))
            # else:
            #     dct[k] = v
        return dct

    class Config:
        arbitrary_types_allowed = True


# User.update_forward_refs()

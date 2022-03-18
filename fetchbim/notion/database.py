from __future__ import annotations

import datetime

from typing import TYPE_CHECKING, Optional
from uuid import UUID


from pydantic import BaseModel

if TYPE_CHECKING:
    from .user import User
    from .rich_text import RichText
    from .file_emoji import FileObject, EmojiObject
    from .property import Property
    from .parent import PageParent, WorkspaceParent


class Database(BaseModel):
    object: str = "database"
    id: UUID | str
    created_time: Optional[datetime.time]
    created_by: Optional[User]
    last_edited_time: Optional[datetime.time]
    last_edited_by: Optional[User]
    title: Optional[list[RichText]]
    icon: Optional[FileObject] | Optional[EmojiObject]
    cover: Optional[FileObject]
    properties: Optional[list[Property]]
    parent: PageParent | WorkspaceParent
    url: str
    archived: bool = False

    class Config:
        arbitrary_types_allowed = True

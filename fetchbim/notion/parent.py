from uuid import UUID

from pydantic import BaseModel


class PageParent(BaseModel):
    type: str = "page_id"
    page_id: UUID | str

    class Config:
        arbitrary_types_allowed = True


class DatabaseParent(BaseModel):
    type: str = "database_id"
    database_id: UUID | str

    class Config:
        arbitrary_types_allowed = True


class WorkspaceParent(BaseModel):
    type: str = "workspace"
    workspace: bool

    class Config:
        arbitrary_types_allowed = True

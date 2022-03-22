from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl


class UserType(str, Enum):
    person = "person"
    bot = "bot"

    def __str__(self):
        return self.value


class User(BaseModel):
    object: str = "user"
    id: UUID | str
    type: Optional[UserType]
    name: Optional[str]
    avatar_url: Optional[HttpUrl]

    class Config:
        use_enum_values = True

    def get_value(self):
        if self.name:
            return self.name
        else:
            return self.id

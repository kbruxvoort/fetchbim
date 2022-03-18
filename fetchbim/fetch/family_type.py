from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from .utils import to_camel
from .parameter import Parameter
from .file import File


class FamilyType(BaseModel):
    id: Optional[str] = None
    name: str
    is_default: Optional[bool] = False
    deleted: bool = False
    files: Optional[list[File]] = []
    parameters: Optional[list[Parameter]] = []

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True

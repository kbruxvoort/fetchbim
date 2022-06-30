from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field
from fetchbim.utils import to_camel
from .parameter import Parameter


class GroupedFamily(BaseModel):
    id: str = Field(None, alias="ChildFamilyId")
    type_id: str = Field(None, alias="FamilyTypeId")
    count: int = Field(1, alias="InstanceCount")
    sort: int = 0
    width: Optional[float] = 0
    depth: Optional[float] = 0
    rotation: Optional[float] = 0
    deleted: bool = False
    parameters: Optional[list[Parameter]] = []
    family_name: Optional[str] = Field(None, alias="ChildFamilyName")
    hosted_families: Optional[list[GroupedFamily]] = Field(
        default_factory=list, alias="ChildModelGroups"
    )

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True

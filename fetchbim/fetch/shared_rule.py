from __future__ import annotations

from typing import Optional
from enum import IntEnum

from pydantic import BaseModel, Field
from fetchbim import client
from .utils import to_camel
from .shared_attribute import SharedAttribute
from .family import ObjectType, Family
from .file import File
from .match_type import MatchType


class SharedRule(BaseModel):
    id: Optional[int] = Field(0, alias="SharedFileId")
    name: str = Field(None, alias="Description")
    category_name: Optional[str] = None
    family_object_type: Optional[ObjectType] = None
    deleted: bool = False
    parameter_name: Optional[str] = None
    parameter_value: Optional[str] = None
    parameter_match_type: Optional[MatchType] = Field(
        None, alias="ParameterValueMatchType"
    )
    files: Optional[list[File]] = []
    attributes: Optional[list[SharedAttribute]] = []

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True

    @classmethod
    def from_id(cls, id: int) -> SharedRule:
        path = f"/SharedFile/{id}"
        response = client.get(path, timeout=30.0)
        response.raise_for_status()
        shared_dict = response.json()
        return cls(**shared_dict)

    def get_families(self) -> list[Family]:
        path = "/SharedFile/Families"
        data = self.dict(
            by_alias=True,
            exclude={"name", "deleted", "files", "attributes", "families"},
        )
        response = client.post(path, json=data, timeout=60.0)
        return [Family(**fam) for fam in response.json()]

    @staticmethod
    def get_shared_rules() -> list[SharedRule]:
        path = f"/SharedFiles"
        response = client.get(path, timeout=None)
        rules = response.json().get("SharedFiles")
        return [SharedRule(**rule) for rule in rules]

    def create(self) -> dict:
        path = f"/SharedFile"
        response = client.post(
            path, json=self.dict(by_alias=True, exclude={"families"})
        )
        return response.json()

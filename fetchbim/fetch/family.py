from __future__ import annotations

from enum import Enum, IntEnum
from typing import Optional

from pydantic import BaseModel
from fetchbim import client
from .utils import to_camel
from .family_type import FamilyType
from .grouped_family import GroupedFamily
from .parameter import Parameter
from .property import Property
from .file import File
from .match_type import MatchType
from .category import Category


class Status(IntEnum):
    PUBLIC = 0
    PRIVATE = 1
    WIP = 2
    WEB = 3

    def __str__(self):
        return self.name.title()


class LoadMethod(IntEnum):
    STANDARD = 0
    DYNAMIC = 1


class ObjectType(str, Enum):
    FAMILY = "Family"
    GROUP = "ModelGroup"
    SCHEDULE = "Schedule"
    TEMPLATE = "Template"

    def __str__(self):
        return self.value


class Family(BaseModel):
    id: Optional[str] = None
    name: str
    category_name: str
    family_object_type: ObjectType = ObjectType.FAMILY
    load_method: LoadMethod = LoadMethod.STANDARD
    status: Status = Status.WIP
    deleted: bool = False
    grouped_families: Optional[list[GroupedFamily]] = []
    files: Optional[list[File]] = []
    family_types: Optional[list[FamilyType]] = []
    properties: Optional[list[Property]] = []
    parameters: Optional[list[Parameter]] = []
    additional_categories: Optional[list[Category]] = []

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True

    @classmethod
    def from_id(cls, id: str) -> Family:
        path = f"v2/Home/Family/{id}"
        response = client.get(path)
        fam_dict = response.json()["BusinessFamilies"][0]
        return cls(**fam_dict)

    def create(self) -> dict:
        path = f"/v2/Family/"
        response = client.post(path, json=self.dict(by_alias=True))
        return response.json()

    def update(self, field_names: list[str]) -> dict:
        path = f"/Family"
        data = self.dict(by_alias=True, include=set(field_names))
        data["FamilyId"] = self.id
        response = client.patch(path, json=data)
        return response.json()

    def delete(self) -> dict:
        path = f"/Family/{self.id}"
        response = client.delete(path)
        return response.json()

    @staticmethod
    def restore(id: str) -> dict:
        path = f"/Family/{id}/Restore"
        response = client.post(path)
        return response.json()

    @staticmethod
    def search(
        family_object_type: Optional[ObjectType] = None,
        category_name: Optional[str] = None,
        parameter_name: Optional[str] = None,
        parameter_value: Optional[str] = None,
        parameter_match_type: Optional[MatchType] = None,
        property_name: Optional[str] = None,
        property_value: Optional[str] = None,
        property_match_type: Optional[MatchType] = None,
        file_key: Optional[str] = None,
    ) -> list[Family]:
        path = "/SharedFile/Families"
        data = {}
        data["FamilyObjectType"] = family_object_type
        data["CategoryName"] = category_name
        data["ParameterName"] = parameter_name
        data["ParameterValue"] = parameter_value
        data["ParameterValueMatchType"] = parameter_match_type
        data["PropertyName"] = property_name
        data["PropertyValue"] = property_value
        data["PropertyValueMatchType"] = property_match_type
        data["FileKey"] = file_key

        response = client.post(path, json=data, timeout=60.0)
        families = response.json()
        return [Family(**fam) for fam in families]

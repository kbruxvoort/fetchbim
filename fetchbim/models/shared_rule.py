from __future__ import annotations

from typing import Optional
from enum import IntEnum

from pydantic import BaseModel, Field

# from fetchbim import client, an_client
from fetchbim.utils import to_camel
from .shared_attribute import SharedAttribute
from .family import ObjectType, Family
from .file import File
from .match_type import MatchType

from ..notion.page import Page


class SharedRule(BaseModel):
    id: Optional[int] = 0
    name: str = ""
    category_name: Optional[str] = None
    family_object_type: Optional[ObjectType] = None
    deleted: bool = False
    parameter_name: Optional[str] = None
    parameter_value: Optional[str] = None
    parameter_match_type: Optional[MatchType] = None
    files: Optional[list[File]] = []
    attributes: Optional[list[SharedAttribute]] = []

    class Config:
        fields = {
            "id": "SharedFileId",
            "name": "Description",
            "parameter_match_type": "ParameterValueMatchType",
        }
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True
        smart_union = True

    #     @classmethod
    #     def from_id(cls, id: int) -> SharedRule:
    #         path = f"/SharedFile/{id}"
    #         response = client.get(path, timeout=30.0)
    #         response.raise_for_status()
    #         shared_dict = response.json()
    #         return cls(**shared_dict)

    @classmethod
    def from_notion_page(cls, client, page: Page) -> SharedRule:
        attributes = None
        attr_ids = page.properties["SharedAttributes"].get_value()
        if attr_ids:
            attr_pages = [
                Page(**client.pages.retrieve(attr_id)) for attr_id in attr_ids
            ]
            attributes = [
                SharedAttribute.from_notion_page(attr_page) for attr_page in attr_pages
            ]
        return cls(
            id=page.properties["SharedFileId"].get_value(),
            name=page.properties["Description"].get_value(),
            category_name=page.properties["CategoryName"].get_value(),
            family_object_type=page.properties["FamilyObjectType"].get_value(),
            deleted=page.properties["Deleted"].get_value(),
            parameter_name=page.properties["ParameterName"].get_value(),
            parameter_value=page.properties["ParameterValue"].get_value(),
            parameter_match_type=page.properties["ParameterValueMatchType"].get_value(),
            files=None,
            attributes=attributes,
        )
        # return cls(**page.dict())


#     def get_families(self) -> list[Family]:
#         path = "/SharedFile/Families"
#         data = self.dict(
#             by_alias=True,
#             exclude={"name", "deleted", "files", "attributes", "families"},
#         )
#         response = client.post(path, json=data, timeout=60.0)
#         return [Family(**fam) for fam in response.json()]

#     @staticmethod
#     def get_shared_rules() -> list[SharedRule]:
#         path = f"/SharedFiles"
#         response = client.get(path, timeout=None)
#         rules = response.json().get("SharedFiles")
#         return [SharedRule(**rule) for rule in rules]

#     def create(self) -> dict:
#         path = f"/SharedFile"
#         response = client.post(
#             path, json=self.dict(by_alias=True, exclude={"families"})
#         )
#         return response.json()

# # async request to get author from book id
# async def get_author_from_book_id(book_id: str) -> str:
#     path = f"/Book/{book_id}/Author"
#     response = await an_client.get(path, timeout=30.0)
#     response.raise_for_status()
#     author = response.json()
#     return author

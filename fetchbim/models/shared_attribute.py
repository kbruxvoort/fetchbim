from __future__ import annotations

import html

from typing import Optional
from enum import IntEnum

from pydantic import BaseModel, Field

# from ..notion.page import Page
from fetchbim.utils import to_camel
from .parameter import ParameterType, DataType


class AttributeType(IntEnum):
    PARAMETER = 0
    PROPERTY = 1


class SharedAttribute(BaseModel):
    id: Optional[int]
    name: str
    value: str
    attribute_type: AttributeType
    sort: int = 0
    hidden: bool = False
    deleted: bool = False
    parameter_type: Optional[ParameterType]
    data_type: Optional[DataType]

    class Config:
        fields = {"id": "SharedAttributeId"}
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True
        smart_union = True

    @classmethod
    def from_notion_page(cls, page: Page) -> SharedAttribute:
        return cls(
            id=int(page.properties["SharedAttributeId"].get_value(default=0)),
            name=page.properties["Name"].get_value(),
            value=html.unescape(page.properties["Value"].get_value()),
            attribute_type=page.properties["AttributeType"].get_value(),
            sort=page.properties["Sort"].get_value(default=0),
            hidden=page.properties["Hidden"].get_value(),
            deleted=page.properties["Deleted"].get_value(),
            parameter_type=page.properties["ParameterType"].get_value(),
            data_type=page.properties["DataType"].get_value(),
        )

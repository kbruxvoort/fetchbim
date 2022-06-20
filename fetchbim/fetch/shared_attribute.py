from __future__ import annotations

from typing import Optional
from enum import IntEnum

from pydantic import BaseModel, Field
from .utils import to_camel
from .parameter import ParameterType, DataType


class AttributeType(IntEnum):
    PARAMETER = 0
    PROPERTY = 1


class SharedAttribute(BaseModel):
    id: Optional[int] = Field(0, alias="SharedAttributeId")
    name: str
    value: str
    attribute_type: AttributeType
    sort: int = 0
    hidden: bool = False
    deleted: bool = False
    parameter_type: Optional[ParameterType]
    data_type: Optional[DataType]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True

    @classmethod
    def from_notion_page(cls, page: Page) -> SharedAttribute:
        return cls(
            name=page.properties["Name"].get_value(),
            value=page.properties["Value"].get_value(),
            attribute_type=page.properties["AttributeType"].get_value(),
            sort=page.properties["Sort"].get_value(),
            hidden=page.properties["Hidden"].get_value(),
            deleted=page.properties["Deleted"].get_value(),
            parameter_type=page.properties["ParameterType"].get_value(),
            data_type=page.properties["DataType"].get_value(),
        )

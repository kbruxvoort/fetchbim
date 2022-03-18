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
    data_Type: Optional[DataType]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True

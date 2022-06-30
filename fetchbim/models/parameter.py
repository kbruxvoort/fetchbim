from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from fetchbim.utils import to_camel


class DataType(str, Enum):
    TEXT = "Text"
    INTEGER = "Integer"
    NUMBER = "Number"
    LENGTH = "Length"
    AREA = "Area"
    VOLUME = "Volume"
    ANGLE = "Angle"
    SLOPE = "Slope"
    CURRENCY = "Currency"
    MASS = "MassDensity"
    URL = "URL"
    BOOLEAN = "Boolean"
    MULTITEXT = "MultlineText"

    def __str__(self):
        return self.value


class ParameterType(str, Enum):
    TYPE = "Type"
    INST = "Instance"

    def __str__(self):
        return self.value


class Parameter(BaseModel):
    id: Optional[int] = Field(default=None, alias="ParameterId")
    name: str
    value: str
    parameter_type: ParameterType = ParameterType.TYPE
    data_type: DataType = DataType.TEXT
    sort: int = 0
    hidden: bool = False

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True

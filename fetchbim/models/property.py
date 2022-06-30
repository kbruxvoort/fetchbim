from typing import Optional

from pydantic import BaseModel
from fetchbim.utils import to_camel


class Property(BaseModel):
    id: Optional[int] = None
    name: str
    value: str
    deleted: bool = False

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True

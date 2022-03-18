from pydantic import BaseModel
from .utils import to_camel


class Category(BaseModel):
    category_type: str
    category_name: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True

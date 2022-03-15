from pprint import pprint
from fetchbim import SharedRule, SharedAttribute, MatchType, AttributeType, ObjectType


attributes = [
    SharedAttribute(
        name="Shared Property", value="API", attribute_type=AttributeType.PROPERTY
    )
]

sr = SharedRule(
    name="API Rule",
    family_object_type=ObjectType.FAMILY,
    parameter_name="API",
    parameter_value="1",
    parameter_match_type=MatchType.EQUALS,
    attributes=attributes,
)

response = sr.create()
pprint(response)

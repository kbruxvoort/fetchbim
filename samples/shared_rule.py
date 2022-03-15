from pprint import pprint
from fetchbim import SharedRule, SharedAttribute, MatchType, AttributeType

attributes = [
    SharedAttribute(
        name="Shared Property", value="API", attribute_type=AttributeType.PROPERTY
    )
]

sr = SharedRule(
    name="API Rule",
    parameter_name="API",
    parameter_value="1",
    parameter_match_type=MatchType.EQUALS,
    attributes=attributes,
)

# pprint(sr.json(by_alias=True, exclude={"families"}))
response = sr.create()
pprint(response)

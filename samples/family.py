from pprint import pprint

from fetchbim import (
    Family,
    FamilyType,
    Parameter,
    Property,
    ParameterType,
    DataType,
)


props = [
    Property(name="TitleHeader", value="Created"),
    Property(name="TitleSubheader", value="Family"),
]

params = [
    Parameter(
        name="Width",
        value="5.0",
        parameter_type=ParameterType.INST,
        data_type=DataType.LENGTH,
    ),
    Parameter(name="Manufacturer", value="Kyle"),
]

type_params = [Parameter(name="Depth", value="2.5", data_type=DataType.LENGTH)]

family_types = [FamilyType(name="Default", is_default=True, parameters=type_params)]

fam = Family(
    name="Created Family",
    category_name="Casework",
    parameters=params,
    properties=props,
    family_types=family_types,
)

response = fam.create()
pprint(response)

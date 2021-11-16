import requests
import json

from . import settings
from .attributes import Property, Parameter, File
from .notion import NotionProperty as np
from .notion import NotionFilter, PropertyType, NotionPage
from .utils import retry
from enum import Enum


class Status(Enum):
    PUBLIC = 0
    PRIVATE = 1
    WIP = 2


class Object(object):
    def __init__(self, Name, Parameters=None):
        self.Name = Name
        if Parameters == None:
            self.Parameters = []
        else:
            self.Parameters = Parameters
        super(Object, self).__init__()

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def add_parameters(self, parameters):
        if not isinstance(parameters, list):
            params = [parameters]
        for param in params:
            if param.Name not in [x.Name for x in self.Parameters]:
                self.Parameters.append(param)
            else:
                print("{} is already in the family").format(param.Name)

    def remove_parameters(self, parameters):
        if not isinstance(parameters, list):
            params = [parameters]
        for param in params:
            for p in self.Parameters:
                if param.Name == p.Name:
                    if p.ParameterId > 0:
                        p.Deleted = True
                    else:
                        self.Parameters.remove(p)

    def add_files(self, files):
        if not isinstance(files, list):
            fls = [files]
        for f in fls:
            for existing_file in self.Files:
                if f.FileKey == existing_file.FileKey:
                    existing_file.Deleted = True
            self.Files.append(f)


class FamilyType(Object):
    def __init__(
        self,
        Name,
        Parameters=None,
        Files=None,
        IsDefault=False,
        Deleted=False,
        Id="",
        FamilyId="",
    ):
        super(FamilyType, self).__init__(Name, Parameters)
        if Files == None:
            self.Files = []
        else:
            self.Files = Files
        self.IsDefault = IsDefault
        self.Deleted = Deleted
        self.Id = Id
        self.FamilyId = FamilyId

    @classmethod
    def from_json(cls, json_dict):
        Id = json_dict.get("Id", "")
        Name = json_dict.get("Name", "")
        Parameters = []
        if json_dict.get("Parameters", []):
            for param in json_dict.get("Parameters", []):
                Parameters.append(Parameter.from_json(param))
        Files = []
        if json_dict.get("Files", []):
            for file in json_dict.get("Files", []):
                Files.append(File.from_json(file))
        IsDefault = json_dict.get("IsDefault", False)
        Deleted = json_dict.get("Deleted", False)

        return cls(Name, Parameters, Files, IsDefault, Deleted, Id)

    @classmethod
    def from_service(cls, json_dict):
        return cls(
            json_dict.get("typeName", ""),
            json_dict.get("parameters", []),
            [],
            False,
            False,
            json_dict.get("familyTypeId", ""),
            json_dict.get("familyId", ""),
        )

    def add_attributes(self, attributes):
        if not isinstance(attributes, list):
            attributes = [attributes]
        for attribute in attributes:
            if attribute.__class__.__name__ == "Parameter" and attribute.ParameterId not in [
                x.ParameterId for x in self.Parameters
            ]:
                self.Parameters.append(attribute)
            elif attribute.__class__.__name__ == "File" and attribute.FileId not in [x.FileId for x in self.Files]:
                self.Files.append(attribute)

    def __repr__(self):
        return "FamilyType(Name={}, Parameters={}, Files={}, IsDefault={}, Deleted={}, Id={}, FamilyId={})".format(
            self.Name,
            self.Parameters,
            self.Files,
            self.IsDefault,
            self.Deleted,
            self.Id,
            self.FamilyId,
        )

    def __str__(self):
        return "[{}: {}]".format(self.Id, self.Name)


class Family(Object):
    def __init__(
        self,
        Name,
        Status=Status.WIP.value,
        LoadMethod=0,
        CategoryName="",
        FamilyObjectType="Family",
        Properties=None,
        Parameters=None,
        Files=None,
        Deleted=False,
        Id="",
        GroupedFamilies=None,
        FamilyTypes=None,
    ):
        super(Family, self).__init__(Name, Parameters)
        self.Status = Status
        self.FamilyObjectType = FamilyObjectType
        self.CategoryName = CategoryName
        self.LoadMethod = LoadMethod
        self.Deleted = Deleted
        self.Id = Id
        if not self.Id:
            self.IsNew = True
        else:
            self.IsNew = False
        if Properties == None:
            self.Properties = []
        else:
            self.Properties = Properties
        if Files == None:
            self.Files = []
        else:
            self.Files = Files
        if GroupedFamilies == None:
            self.GroupedFamilies = []
        else:
            self.GroupedFamilies = GroupedFamilies
        if FamilyTypes == None:
            self.FamilyTypes = []
        else:
            self.FamilyTypes = FamilyTypes

    @retry
    def post(self):
        data = self.to_json()
        url = settings.POST_FAMILY
        headers = settings.BIM_HEADERS
        response = requests.post(url, data=data, headers=headers)
        if response.status_code in range(200, 299):
            result = response.json()
            self.Id = result.get("Id", "")
            self.Name = result.get("Name", "")
            self.Status = result.get("Status")
            self.LoadMethod = result.get("LoadMethod")
            self.CategoryName = result.get("CategoryName", "")
            self.FamilyObjectType = result.get("FamilyObjectType")
            self.Properties = []
            for prop in result.get("Properties", []):
                self.add_properties(Property.from_json(prop))
            self.Parameters = []
            for param in result.get("Parameters", []):
                self.add_parameters(Parameter.from_json(param))
            self.Files = []
            for file in result.get("Files", []):
                self.add_files(File.from_json(file))
            self.GroupedFamilies = []
            for fam in result.get("GroupedFamilies", []):
                self.GroupedFamilies.append(Family.from_json(fam))
            self.FamilyTypes, Type_Params = [], []
            for ft in result.get("FamilyTypes", []):
                for type_param in ft.get("Parameters"):
                    Type_Params.append(Parameter.from_json(type_param))
                ft["Parameters"] = Type_Params
                self.add_type(FamilyType.from_json(ft))
            self.Deleted = result.get("Deleted")
        else:
            print(response.text)

    # TODO: add other file data
    def to_notion(self):
        data = {"properties": {}}
        data["archived"] = False
        if any(x for x in self.Files if x.FileKey == "FamilyImageLarge"):
            image_url = "https://bimservice.ssgbim.com:443/Family/{}/File/FamilyImageLarge".format(self.Id)
            data["cover"] = {"type": "external", "external": {"url": image_url}}
        np.set_property(data, self.Name, "Name", "title")
        np.set_property(data, self.Id, "SSGFID")
        # prop.set_property(data, self.CategoryName, '_Revit Category', 'relation') RELATION
        if self.Status == 0:
            _status = "Public"
        elif self.Status == 1:
            _status = "Private"
        else:
            _status = "Work in Progress"
        np.set_property(data, _status, "_Status", "select")

        # Properties
        detail = self.get_property("Detail")
        tech_data = self.get_property("Technical Data")
        fam_design = self.get_property("Family Design")
        tags = self.get_property("Tags")
        includes_pricing = self.get_property("Includes Pricing")
        ada_compliant = self.get_property("ADA Compliant")
        has_connectors = self.get_property("Has MEP Connectors")
        product_id = self.get_property("product_id")

        if detail is not None:
            np.set_property(data, detail.Value, "_Detail")
        if tech_data is not None:
            np.set_property(data, tech_data.Value, "_Technical Data")
        if fam_design is not None:
            np.set_property(data, fam_design.Value, "_Family Design")
        if tags is not None:
            np.set_property(data, tags.Value.replace(",", "\n"), "_Tags")
        if includes_pricing is not None:
            if includes_pricing == "Yes":
                v1 = True
            else:
                v1 = False
            np.set_property(data, v1, "_Includes Pricing", "checkbox")
        if ada_compliant is not None:
            if ada_compliant == "Yes":
                v2 = True
            else:
                v2 = False
            np.set_property(data, v2, "_ADA Compliant", "checkbox")
        if has_connectors is not None:
            if has_connectors == "Yes":
                v3 = True
            else:
                v3 = False
            np.set_property(data, v3, "_Has MEP Connectors", "checkbox")
        if product_id is not None:
            product_page = "https://fetchbim.com/catalog/product/view/id/"
            np.set_property(data, product_page + product_id.Value, "_Product Page", "url")

        relation_properties = [
            {
                "value": self.CategoryName.split("/")[0],
                "db_name": "Revit Categories",
                "prop_name": "Category",
                "field_name": "_Revit Category",
            },
            {
                "value": self.get_property("Omniclass"),
                "db_name": "BIMobject Omniclass",
                "prop_name": "code",
                "field_name": "_Omniclass",
            },
            {
                "value": self.get_property("BIMobject Category"),
                "db_name": "BIMobject Categories",
                "prop_name": "Combined Name",
                "field_name": "_BIMobject Category",
            },
            {
                "value": self.get_property("IFC"),
                "db_name": "BIMobject IFC",
                "prop_name": "name",
                "field_name": "_IFC",
            },
            {
                "value": self.get_property("Keynote"),
                "db_name": "BIMobject Masterformat2014",
                "prop_name": "name",
                "field_name": "_Masterformat",
            },
            {
                "value": self.get_property("Assembly Code"),
                "db_name": "BIMobject Uniformat2",
                "prop_name": "name",
                "field_name": "_Uniformat",
            },
            {
                "value": [x.ChildFamilyId for x in self.GroupedFamilies],
                "db_name": "Content Calendar",
                "prop_name": "SSGFID",
                "field_name": "_Families in Model Group",
            },
        ]

        for relation in relation_properties:
            value = relation.get("value")
            if value:
                if isinstance(value, Property):
                    value = value.Value
                notion_filter = NotionFilter(value, property_name=relation["prop_name"])
                filter_results = notion_filter.query(relation["db_name"])
                np.set_property(
                    data,
                    filter_results,
                    relation["field_name"],
                    property_type=PropertyType.RELATION,
                )

        return data

    def post_notion(self):
        data = self.to_notion()
        exists_filter = NotionFilter(self.Id, property_name="SSGFID")
        exists = exists_filter.query("Content Calendar")
        if exists:
            return NotionPage.update(exists[0].get("id"), data)
        else:
            return NotionPage.create("Content Calendar", data)

    @retry
    def delete(self):
        self.Deleted = True
        url = settings.DELETE_FAMILY.format(self.Id)
        headers = settings.BIM_HEADERS
        return requests.delete(url, headers=headers)

    @retry
    def restore(self):
        self.Deleted = False
        url = settings.RESTORE_FAMILY.format(self.Id)
        headers = settings.BIM_HEADERS
        return requests.post(url, headers=headers)

    @staticmethod
    @retry
    def get_json(guid):
        response = requests.get(settings.GET_FULL_FAMILY.format(guid), headers=settings.BIM_HEADERS)
        if response.status_code in range(200, 299):
            try:
                return response.json()["BusinessFamilies"][0]
            except IndexError as e:
                print(e)

    @classmethod
    def from_json(cls, json_dict):
        Id = json_dict.get("Id", "")
        Name = json_dict.get("Name", "")
        Status = json_dict.get("Status")
        LoadMethod = json_dict.get("LoadMethod")
        CategoryName = json_dict.get("CategoryName", "")
        FamilyObjectType = json_dict.get("FamilyObjectType")
        Properties = []
        if json_dict.get("Properties", []):
            for prop in json_dict.get("Properties", []):
                Properties.append(Property.from_json(prop))
        Parameters = []
        if json_dict.get("Parameters", []):
            for param in json_dict.get("Parameters", []):
                Parameters.append(Parameter.from_json(param))
        Files = []
        if json_dict.get("Files", []):
            for file in json_dict.get("Files", []):
                Files.append(File.from_json(file))
        Deleted = json_dict.get("Deleted")
        GroupedFamilies = []
        if json_dict.get("GroupedFamilies", []):
            for fam in json_dict.get("GroupedFamilies", []):
                GroupedFamilies.append(GroupedFamily.from_json(fam))
        FamilyTypes = []
        if json_dict.get("FamilyTypes", []):
            for fam_type in json_dict.get("FamilyTypes", []):
                f_type = FamilyType.from_json(fam_type)
                f_type.FamilyId = Id
                FamilyTypes.append(f_type)

        return cls(
            Name,
            Status,
            LoadMethod,
            CategoryName,
            FamilyObjectType,
            Properties,
            Parameters,
            Files,
            Deleted,
            Id,
            GroupedFamilies,
            FamilyTypes,
        )

    @classmethod
    def from_service(cls, json_dict):
        Id = json_dict.get("familyId", "")
        Name = json_dict.get("familyName", "")
        Status = json_dict.get("status")
        LoadMethod = json_dict.get("loadMethod")
        CategoryName = json_dict.get("categoryName", "")
        FamilyObjectType = json_dict.get("familyObjectType")
        Properties = []
        if json_dict.get("properties", []):
            for prop in json_dict.get("properties", []):
                # add from service to property
                Properties.append(Property.from_json(prop))
        Parameters = []
        for param in json_dict.get("familyParameters", []):
            # add from_service to parameter
            Parameters.append(Parameter.from_json(param))
        Files = []
        for file in json_dict.get("familyFiles", []):
            # add from_service to file
            Files.append(File.from_json(file))
        # Deleted = json_dict.get('Deleted')
        GroupedFamilies = []
        for fam in json_dict.get("groupedFamilies", []):
            # add from service to grouped family
            GroupedFamilies.append(Family.from_json(fam))
        FamilyTypes = []
        for fam_type in json_dict.get("familyTypes", []):
            # add from service to family types
            f_type = FamilyType.from_json(fam_type)
            f_type.Parameters = []
            for param in fam_type.get("parameters", []):
                f_type.Parameters.append(Parameter.from_json(param))
            FamilyTypes.append(f_type)

        return cls(
            Name,
            Status,
            LoadMethod,
            CategoryName,
            FamilyObjectType,
            Properties,
            Parameters,
            Files,
            False,
            Id,
            GroupedFamilies,
            FamilyTypes,
        )

    def add_type(self, fam_type):
        names = [ftype.Name for ftype in self.FamilyTypes]
        if fam_type.Name not in names:
            fam_type.FamilyId = self.Id
            self.FamilyTypes.append(fam_type)
        else:
            print("{} already exists in family").format(fam_type.Name)

    def get_property(self, name, default=None):
        prop = [x for x in self.Properties if x.Name == name and x.Value]
        if prop:
            return prop[0]
        else:
            return default

    def get_parameter(self, name):
        param = [x for x in self.Parameters if x.Name == name]
        if len(param) == 1:
            return param[0]
        else:
            return param

    def get_file(self, name):
        return [x for x in self.Files if x.FileName == name]

    def add_properties(self, properties):
        if not isinstance(properties, list):
            props = [properties]
        for prop in props:
            if prop.Name not in [x.Name for x in self.Properties]:
                self.Properties.append(prop)
            else:
                print("{} is already in the family").format(prop.Name)

    def __repr__(self):
        return "Family(Name={}, Status={}, LoadMethod={}, CategoryName={}, FamilyObjectType={}, Properties={}, Parameters={}, Files={}, Deleted={}, Id={}, GroupedFamilies={}, FamilyTypes={})".format(
            self.Name,
            self.Status,
            self.LoadMethod,
            self.CategoryName,
            self.FamilyObjectType,
            self.Properties,
            self.Parameters,
            self.Files,
            self.Deleted,
            self.Id,
            self.GroupedFamilies,
            self.FamilyTypes,
        )

    def __str__(self):
        return "[{}]: {}".format(self.Id, self.Name)


class GroupedFamily:
    def __init__(
        self,
        ChildFamilyId,
        FamilyTypeId,
        ChildFamilyName=None,
        InstanceCount=1,
        Deleted=False,
        Sort=0,
        Width=0,
        Depth=0,
        Rotation=0,
        Parameters=None,
        ChildModelGroups=None,
    ):
        self.ChildFamilyName = ChildFamilyName
        self.ChildFamilyId = ChildFamilyId
        self.FamilyTypeId = FamilyTypeId
        self.InstanceCount = InstanceCount
        self.Deleted = Deleted
        self.Sort = Sort
        self.Width = Width
        self.Depth = Depth
        self.Rotation = Rotation
        if Parameters == None:
            self.Parameters = []
        else:
            self.Parameters = Parameters
        if ChildModelGroups == None:
            self.ChildModelGroups = []
        else:
            self.ChildModelGroups = ChildModelGroups

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    @classmethod
    def from_json(cls, json_dict):
        ChildFamilyId = json_dict.get("ChildFamilyId")
        FamilyTypeId = json_dict.get("FamilyTypeId")
        ChildFamilyName = json_dict.get("ChildFamilyId")
        InstanceCount = json_dict.get("InstanceCount", 1)
        Deleted = json_dict.get("Deleted", False)
        Sort = json_dict.get("Sort", 0)
        Width = json_dict.get("Width", 0)
        Depth = json_dict.get("Depth", 0)
        Rotation = json_dict.get("Rotation", 0)
        Parameters = json_dict.get("Parameters", [])
        ChildModelGroups = json_dict.get("ChildModelGroups", [])

        return cls(
            ChildFamilyId,
            FamilyTypeId,
            ChildFamilyName,
            InstanceCount,
            Deleted,
            Sort,
            Width,
            Depth,
            Rotation,
            Parameters,
            ChildModelGroups,
        )

    @classmethod
    def from_service(cls, json_dict):
        ChildFamilyId = json_dict.get("childFamilyId")
        ChildFamily = json_dict.get("childFamily")
        if ChildFamily:
            ChildFamilyName = ChildFamily.get("familyName")
            ChildFamilyTypes = ChildFamily.get("FamilyType")
            if ChildFamilyTypes:
                FamilyTypeId = ChildFamilyTypes[0].get("familyTypeId")

        InstanceCount = json_dict.get("instanceCount", 1)
        Sort = json_dict.get("sort", 0)
        Width = json_dict.get("width", 0)
        Depth = json_dict.get("depth", 0)
        Rotation = json_dict.get("rotation", 0)
        Parameters = json_dict.get("parameters", [])

        return cls(
            ChildFamilyId,
            FamilyTypeId,
            ChildFamilyName,
            InstanceCount,
            False,
            Sort,
            Width,
            Depth,
            Rotation,
            Parameters,
        )

    def __repr__(self):
        return "GroupedFamily(ChildFamilyId={}, FamilyTypeId={}, ChildFamilyName={}, InstanceCount={}, Deleted={}, Sort={}, Width={}, Depth={}, Rotation={}, Parameters={}, ChildModelGroups={})".format(
            self.ChildFamilyId,
            self.FamilyTypeId,
            self.ChildFamilyName,
            self.InstanceCount,
            self.Deleted,
            self.Sort,
            self.Width,
            self.Depth,
            self.Rotation,
            self.Parameters,
            self.ChildModelGroups,
        )

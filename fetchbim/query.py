import requests
import json

from . import settings
from .family import Family
from .notion import NotionProperty, NotionPage, NotionFilter, PropertyType, Condition
from .attributes import Parameter, File
from .utils import retry
from enum import Enum


class MatchType(Enum):
    EQUALS = 0
    STARTS = 1
    ENDS = 2
    CONTAINS = 3


class Filter(object):
    def __init__(
        self,
        FamilyObjectType=None,
        CategoryName=None,
        ParameterName=None,
        ParameterValue=None,
        ParameterValueMatchType=None,
        PropertyName=None,
        PropertyValue=None,
        PropertyValueMatchType=None,
        FileKey=None,
    ):
        super(Filter, self).__init__()
        self.FamilyObjectType = FamilyObjectType
        self.CategoryName = CategoryName
        self.ParameterName = ParameterName
        self.ParameterValue = ParameterValue
        self.ParameterValueMatchType = ParameterValueMatchType
        self.PropertyName = PropertyName
        self.PropertyValue = PropertyValue
        self.PropertyValueMatchType = PropertyValueMatchType
        self.FileKey = FileKey

    @classmethod
    def param_exists(cls, name):
        return cls(ParameterName=name, ParameterValue="", ParameterValueMatchType=3)

    @classmethod
    def prop_exists(cls, name):
        return cls(PropertyName=name, PropertyValue="", PropertyValueMatchType=3)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    @retry
    def query(self):
        url = settings.QUERY_FAMILIES
        data = self.to_json()
        headers = settings.BIM_HEADERS
        response = requests.post(url, data=data, headers=headers)
        return response.json()

    def get_ids(self):
        id_list = []
        families = self.query()
        for fam in families:
            id_list.append(fam["Id"])
        return id_list

    def __repr__(self):
        return "Filter(FamilyObjectType={}, CategoryName={}, ParameterName={}, ParameterValue={}, ParameterValueMatchType={}, PropertyName={}, PropertyValue={}, PropertyValueMatchType={}, FileKey={})".format(
            self.FamilyObjectType,
            self.CategoryName,
            self.ParameterName,
            self.ParameterValue,
            self.ParameterValueMatchType,
            self.PropertyName,
            self.PropertyValue,
            self.PropertyValueMatchType,
            self.FileKey,
        )

    # TODO make sure parameters are being returned in get_json method
    # TODO move to admin module
    @staticmethod
    def delete_parameter_by_name(id_list, name_list):
        if not isinstance(name_list, list):
            name_list = [name_list]
        if not isinstance(id_list, list):
            id_list = [id_list]
        for id_ in id_list:
            response = Family.get_json(id_)
            parameters = response["Parameters"]
            for param in parameters:
                if param["Name"] in name_list:
                    param["Deleted"] = True
            requests.post(
                settings.POST_FAMILY,
                data=json.dumps(response),
                headers=settings.BIM_HEADERS,
            )


class SharedFile(Filter):
    def __init__(
        self,
        Description,
        FamilyObjectType=None,
        CategoryName="",
        ParameterName=None,
        ParameterValue=None,
        ParameterValueMatchType=None,
        PropertyName=None,
        PropertyValue=None,
        PropertyValueMatchType=None,
        FileKey=None,
        Deleted=False,
        SharedFileId=0,
        Files=None,
        Attributes=None,
    ):
        super(SharedFile, self).__init__(
            FamilyObjectType,
            CategoryName,
            ParameterName,
            ParameterValue,
            ParameterValueMatchType,
            PropertyName,
            PropertyValue,
            PropertyValueMatchType,
            FileKey,
        )
        self.Description = Description
        self.Deleted = Deleted
        self.SharedFileId = SharedFileId
        if Files == None:
            self.Files = []
        else:
            self.Files = Files
        if Attributes == None:
            self.Attributes = []
        else:
            self.Attributes = Attributes
        self.NotionPageId = None
        self.NotionParentId = None

    @retry
    def post(self):
        data = self.to_json()
        url = settings.GET_SHARED_FILE.format("")
        headers = settings.BIM_HEADERS
        response = requests.post(url, data=data, headers=headers)
        if response.status_code in range(200, 299):
            results = response.json()

            self.Description = results.get("Description", "")
            self.FamilyObjectType = results.get("FamilyObjectType")
            self.CategoryName = results.get("CategoryName", "")
            self.ParameterName = results.get("ParameterName")
            self.ParameterValue = results.get("ParameterValue")
            self.ParameterValueMatchType = results.get("ParameterValueMatchType")
            self.PropertyName = results.get("PropertyName")
            self.PropertyValue = results.get("PropertyValue")
            self.PropertyValueMatchType = results.get("PropertyValueMatchType")
            self.FileKey = results.get("FileKey")
            self.Deleted = results.get("Deleted", False)
            self.SharedFileId = results.get("SharedFileId", 0)
            self.Files = []
            for file in results.get("Files", []):
                self.Files.append(File.from_json(file))
            for attr in self.Attributes:
                for attribute in results.get("Attributes", []):
                    if attr.Name == attribute["Name"]:
                        attr.SharedAttributeId = attribute["SharedAttributeId"]
        else:
            print(response.text)
        return response

    @staticmethod
    @retry
    def get_all():
        url = settings.ALL_SHARED_FILES
        headers = settings.BIM_HEADERS
        response = requests.get(url, headers=headers)
        if response.status_code in range(200, 299):
            response_json = response.json()
            return response_json.get("SharedFiles", [])

    @classmethod
    @retry
    def get_json(cls, SharedFileId):
        url = settings.GET_SHARED_FILE.format(str(SharedFileId))
        headers = settings.BIM_HEADERS
        response = requests.get(url, headers=headers)
        if response.status_code in range(200, 299):
            return response.json()

    @classmethod
    def from_json(cls, SharedFileId):
        result = cls.get_json(str(SharedFileId))
        Description = result.get("Description", "")
        FamilyObjectType = result.get("FamilyObjectType")
        CategoryName = result.get("CategoryName")
        ParameterName = result.get("ParameterName")
        ParameterValue = result.get("ParameterValue")
        ParameterValueMatchType = result.get("ParameterValueMatchType")
        PropertyName = result.get("PropertyName")
        PropertyValue = result.get("PropertyValue")
        PropertyValueMatchType = result.get("PropertyValueMatchType")
        FileKey = result.get("FileKey")
        Deleted = result.get("Deleted")
        SharedFileId = result.get("SharedFileId")
        Files = result.get("Files")
        Attributes = []
        for attribute in result.get("Attributes"):
            Attributes.append(SharedAttribute.from_json(attribute))

        return cls(
            Description,
            FamilyObjectType,
            CategoryName,
            ParameterName,
            ParameterValue,
            ParameterValueMatchType,
            PropertyName,
            PropertyValue,
            PropertyValueMatchType,
            FileKey,
            Deleted,
            SharedFileId,
            Files,
            Attributes,
        )

    @retry
    def to_notion(self):
        data = {"properties": {}}
        data["archived"] = False
        NotionProperty.set_property(data, self.Description, "Description", property_type="title")
        NotionProperty.set_property(data, self.SharedFileId, "SharedFileId", property_type="number")
        if self.FamilyObjectType:
            NotionProperty.set_property(data, self.FamilyObjectType, "FamilyObjectType", property_type="select")
        NotionProperty.set_property(data, self.CategoryName, "CategoryName")
        NotionProperty.set_property(data, self.ParameterName, "ParameterName")
        NotionProperty.set_property(data, self.ParameterValue, "ParameterValue")
        NotionProperty.set_property(data, self.Deleted, "Deleted", property_type="checkbox")
        value = None
        if self.ParameterValueMatchType == 0:
            value = "Equals"
        elif self.ParameterValueMatchType == 1:
            value = "StartsWith"
        elif self.ParameterValueMatchType == 2:
            value = "EndsWith"
        elif self.ParameterValueMatchType == 3:
            value = "Contains"
        # NotionProperty.set_property(data, value, "ParameterValueMatchType", "select")
        NotionProperty.set_property(data, value, "MatchType", property_type="select")
        SharedAttributes = []
        if self.Attributes:
            for attribute in self.Attributes:
                response = attribute.to_notion()
                response_json = response.json()
                SharedAttributes.append(response_json)
            NotionProperty.set_property(data, SharedAttributes, "SharedAttributes", property_type="relation")

        exists_filter = NotionFilter(self.SharedFileId, filter_type=PropertyType.NUMBER, property_name="SharedFileId")
        exists = exists_filter.query("Shared Rules")
        if exists:
            r = NotionPage.update(exists[0].get("id"), data)
        else:
            r = NotionPage.create("Shared Rules", data)

    @classmethod
    @retry
    def from_notion(cls, json_dict):
        NotionPageId = json_dict["id"]
        NotionParentId = json_dict["parent"]["database_id"]
        props = json_dict["properties"]

        Description = NotionProperty.get_property(props, "Description", "")
        FamilyObjectType = NotionProperty.get_property(props, "FamilyObjectType", None)
        CategoryName = NotionProperty.get_property(props, "CategoryName", None)
        ParameterName = NotionProperty.get_property(props, "ParameterName", "")
        ParameterValue = NotionProperty.get_property(props, "ParameterValue", "")
        ParameterValueMatchType = NotionProperty.get_property(props, "ParameterValueMatchType", 0)
        Deleted = NotionProperty.get_property(props, "Deleted", False)
        SharedFileId = NotionProperty.get_property(props, "SharedFileId", 0)
        AttributesProp = NotionProperty.get_property(props, "SharedAttributes")
        Attributes = []
        if AttributesProp:
            for id_ in AttributesProp:
                url = settings.NOTION_PAGE + id_
                response = requests.get(url, headers=settings.NOTION_HEADERS)
                if response.status_code in range(200, 299):
                    results = response.json()
                    shared_attribute = SharedAttribute.from_notion(results)
                    Attributes.append(shared_attribute)
                else:
                    print(response.text)

        shared_file = cls(
            Description=Description,
            FamilyObjectType=FamilyObjectType,
            CategoryName=CategoryName,
            ParameterName=ParameterName,
            ParameterValue=ParameterValue,
            ParameterValueMatchType=ParameterValueMatchType,
            PropertyName=None,
            PropertyValue=None,
            PropertyValueMatchType=None,
            FileKey=None,
            Deleted=Deleted,
            SharedFileId=SharedFileId,
            Files=None,
            Attributes=Attributes,
        )
        shared_file.NotionPageId = NotionPageId
        shared_file.NotionParentId = NotionParentId

        return shared_file

    @staticmethod
    @retry
    def archive_notion(db_name):
        no_filter = NotionFilter(None)
        results = no_filter.query(db_name)
        for r in results:
            NotionPage.archive(r["id"])

    @staticmethod
    def archive_db(id_list):
        pass

    def __repr__(self):
        return "SharedFile(Description={}, FamilyObjectType={}, CategoryName={}, ParameterName={}, ParameterValue={}, ParameterValueMatchType={}, PropertyName={}, PropertyValue={}, PropertyValueMatchType={}, FileKey={}, Deleted={}, SharedFileId={}, Files={}, Attributes={})".format(
            self.Description,
            self.FamilyObjectType,
            self.CategoryName,
            self.ParameterName,
            self.ParameterValue,
            self.ParameterValueMatchType,
            self.PropertyName,
            self.PropertyValue,
            self.PropertyValueMatchType,
            self.FileKey,
            self.Deleted,
            self.SharedFileId,
            self.Files,
            self.Attributes,
        )


class SharedAttribute(Parameter):
    def __init__(
        self,
        Name,
        Value,
        Deleted=False,
        DataType=None,
        ParameterType=None,
        Sort=0,
        Hidden=False,
        ParameterId=0,
        AttributeType=0,
        SharedAttributeId=0,
    ):
        super(SharedAttribute, self).__init__(Name, Value, Deleted, DataType, ParameterType, Sort, Hidden, ParameterId)
        self.AttributeType = AttributeType
        self.SharedAttributeId = SharedAttributeId
        self.NotionPageId = None
        self.NotionParentId = None

    @classmethod
    def from_json(cls, json_dict):
        Name = json_dict.get("Name", "")
        Value = json_dict.get("Value", "")
        Deleted = json_dict.get("Deleted", False)
        DataType = json_dict.get("DataType")
        ParameterType = json_dict.get("ParameterType")
        Sort = json_dict.get("Sort")
        Hidden = json_dict.get("Hidden", False)
        ParameterId = json_dict.get("ParameterId", 0)
        AttributeType = json_dict.get("AttributeType")
        SharedAttributeId = json_dict.get("SharedAttributeId", 0)
        NotionPageId = json_dict.get("NotionPageId")
        NotionParentId = json_dict.get("NotionParentId")

        shared_attr = cls(
            Name,
            Value,
            Deleted,
            DataType,
            ParameterType,
            Sort,
            Hidden,
            ParameterId,
            AttributeType,
            SharedAttributeId,
        )
        shared_attr.NotionPageId = NotionPageId
        shared_attr.NotionParentId = NotionParentId

        return shared_attr

    def to_notion(self):
        data = {"properties": {}}
        data["archived"] = False
        data["properties"]["SharedAttributeId"] = {"number": self.SharedAttributeId}
        value = None
        if self.AttributeType == 0:
            value = "Parameter"
        elif self.AttributeType == 1:
            value = "Property"
        if value:
            NotionProperty.set_property(data, value, "AttributeTypeDescription", "select")
        NotionProperty.set_property(data, self.Name, "Name", "title")
        NotionProperty.set_property(data, self.Value, "Value")
        NotionProperty.set_property(data, self.Deleted, "Deleted", "checkbox")
        if self.DataType:
            NotionProperty.set_property(data, self.DataType, "DataType", "select")
        if self.ParameterType:
            NotionProperty.set_property(data, self.ParameterType, "ParameterType", "select")
        NotionProperty.set_property(data, self.Sort, "Sort", "number")
        NotionProperty.set_property(data, self.Hidden, "Hidden", "checkbox")

        # print(data)
        # print(self.NotionPageId)

        exists_filter = NotionFilter(
            self.SharedAttributeId, filter_type=PropertyType.NUMBER, property_name="SharedAttributeId"
        )
        exists = exists_filter.query("Shared Attributes")
        if exists:
            return NotionPage.update(exists[0].get("id"), data)
        else:
            return NotionPage.create("Shared Attributes", data)
        # print(r.json())

    @classmethod
    def from_notion(cls, json_dict):
        NotionPageId = json_dict["id"]
        NotionParentId = json_dict["parent"]["database_id"]
        props = json_dict["properties"]

        Name = NotionProperty.get_property(props, "Name", "")
        Value = NotionProperty.get_property(props, "Value", "")
        Deleted = NotionProperty.get_property(props, "Deleted", False)
        DataType = NotionProperty.get_property(props, "DataType")
        ParameterType = NotionProperty.get_property(props, "ParameterType")
        Sort = NotionProperty.get_property(props, "Sort")
        Hidden = NotionProperty.get_property(props, "Hidden", False)
        ParameterId = 0
        AttributeType = NotionProperty.get_property(props, "AttributeType", 0)
        SharedAttributeId = NotionProperty.get_property(props, "SharedAttributeId", 0)

        shared_attr = cls(
            Name,
            Value,
            Deleted,
            DataType,
            ParameterType,
            Sort,
            Hidden,
            ParameterId,
            AttributeType,
            SharedAttributeId,
        )
        shared_attr.NotionPageId = NotionPageId
        shared_attr.NotionParentId = NotionParentId

        return shared_attr

    def __repr__(self):
        return "SharedAttribute(Name={}, Value={}, Deleted={}, DataType={}, ParameterType={}, Sort={}, Hidden={}, ParameterId={}, AttributeType={}, SharedAttributeId={})".format(
            self.Name,
            self.Value,
            self.Deleted,
            self.DataType,
            self.ParameterType,
            self.Sort,
            self.Hidden,
            self.ParameterId,
            self.AttributeType,
            self.SharedAttributeId,
        )

    def __str__(self):
        return "[{}] {}: {}".format(self.SharedAttributeId, self.Name, self.Value)

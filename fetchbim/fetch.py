import json
import base64
import tkinter
import sys

from tkinter import filedialog
from typing import Any, Dict, List, Optional, Type, Union

from . import client, dev_client


def json_class_parse(object_class, lookup_value, json_dict) -> List:
    if lookup_value in json_dict:
        if isinstance(json_dict[lookup_value], list):
            return [object_class.from_dict(x) for x in json_dict[lookup_value]]
        else:
            return [object_class.from_dict(json_dict[lookup_value])]


class FetchModel(object):

    """Base class from which all Fetch models will inherit."""

    def __init__(self, **kwargs):
        self.param_defaults = {}

    def __str__(self):
        return json.dumps(self.to_dict(), sort_keys=True)

    def __hash__(self):
        if hasattr(self, "id"):
            return hash(self.id)
        else:
            raise TypeError(f"unhashable type: {type(self)} (no id attribute)")

    def to_dict(self):
        """Create a dictionary representation of the object. Please see inline
        comments on construction when dictionaries contain TwitterModels."""
        data = {}

        for (key, value) in self.param_defaults.items():

            # If the value is a list, we need to create a list to hold the
            # dicts created by an object supporting the to_dict() method,
            # i.e., if it inherits from TwitterModel. If the item in the list
            # doesn't support the to_dict() method, then we assign the value
            # directly. An example being a list of Media objects contained
            # within a Status object.
            if isinstance(getattr(self, key, None), (list, tuple, set)):
                data[key] = list()
                for subobj in getattr(self, key, None):
                    if getattr(subobj, "to_dict", None):
                        data[key].append(subobj.to_dict())
                    else:
                        data[key].append(subobj)

            # Not a list, *but still a subclass of TwitterModel* and
            # and we can assign the data[key] directly with the to_dict()
            # method of the object. An example being a Status object contained
            # within a User object.
            elif getattr(getattr(self, key, None), "to_dict", None):
                data[key] = getattr(self, key).to_dict()

            # If the value doesn't have an to_dict() method, i.e., it's not
            # something that subclasses TwitterModel, then we can use direct
            # assignment.
            elif getattr(self, key, None):
                data[key] = getattr(self, key, None)
        return data

    @classmethod
    def from_dict(cls, data, **kwargs):
        """Create a new instance based on a JSON dict. Any kwargs should be
        supplied by the inherited, calling class.
        Args:
            data: A JSON dict, as converted from the JSON in the twitter API.
        """

        json_data = data.copy()
        if kwargs:
            for key, val in kwargs.items():
                json_data[key] = val

        c = cls(**json_data)
        c._json = data
        return c


class Property(FetchModel):
    """A class representing a property of a family"""

    def __init__(self, **kwargs):
        self.param_defaults = {
            "Name": None,
            "Value": None,
            "Id": None,
            "Deleted": False,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return (
            f"Property(Name={self.Name}, "
            f"Value={self.Value}, "
            f"Id={self.Id}, "
            f"Deleted={self.Deleted})"
        )


class Parameter(FetchModel):
    """A class representing a parameter of a family"""

    def __init__(self, **kwargs):
        self.param_defaults = {
            "Name": None,
            "Value": None,
            "ParameterId": None,
            "Deleted": False,
            "DataType": None,
            "ParameterType": None,
            "Sort": 0,
            "Hidden": False,
            "ParameterId": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return (
            f"Parameter(Name={self.Name}, "
            f"Value={self.Value}, "
            f"Deleted={self.Deleted}, "
            f"DataType={self.DataType}, "
            f"ParameterType={self.ParameterType}, "
            f"Sort={self.Sort}, "
            f"Hidden={self.Hidden}, "
            f"ParameterId={self.ParameterId})"
        )


# Might deprecate this with new file endpoint
class File(FetchModel):
    """A class representing a file of a family"""

    def __init__(self, **kwargs):
        self.param_defaults = {
            "FileId": None,
            "FilePath": None,
            "FileKey": None,
            "FileName": None,
            "FileExtension": None,
            "FileLength": None,
            "Version": None,
            "FileData": None,
            "Deleted": False,
            "FamilyFileIds": None,
            "SharedFileIds": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def file_from_path(self):
        try:
            with open(self.FilePath, "rb") as file:
                byteform = base64.b64encode(file.read())
                self.FileData = byteform.decode("utf-8")
        except TypeError as e:
            print(f"File path is incorrect: {e}")

    @classmethod
    def pick_file(cls):
        root = tkinter.Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename()
        file_ext = file_path.split(".")[-1]
        file_name = file_path.split("/")[-1].split(".")[0]
        c = cls(FilePath=file_path, FileExtension=file_ext, FileName=file_name)
        c.file_from_path()
        return c

    def attach_to_family(self, FamilyIds: List[str], FileId=None):
        path = "/FamilyFiles"
        if FileId is None:
            FileId = self.FileId
        if not isinstance(FamilyIds, list):
            FamilyIds = [FamilyIds]
        data = [{"FamilyId": FamilyId, "FileId": self.FileId} for FamilyId in FamilyIds]
        response = dev_client.post(path, data=json.dumps(data))
        return response.json()

    def length_to_kb(self):
        return int(self.FileLength / 1024)

    @classmethod
    def from_id(cls, file_id):
        path = "/Files"
        params = {"FileId": file_id}
        response = dev_client.get(path, params=params)
        file_dict = response.json()
        if isinstance(file_dict, list):
            try:
                file_dict = file_dict[0]
            except IndexError as e:
                print(f"No file found with FileId: {file_id}")
                return None
        # print(file_dict)
        return File.from_dict(file_dict)

    def update(self, FileName=None, FileKey=None):
        path = "/File"
        data = {}
        data["FileId"] = self.FileId
        if FileName:
            data["FileName"] = FileName
        if FileKey:
            data["FileKey"] = FileKey
        response = dev_client.patch(path, data=json.dumps(data))
        return response.json()

    def replace(self, **kwargs):
        path = f"/File/{self.FileId}"
        data = {}
        if self.FileData is None:
            self.file_from_path()
        if self.FileData:
            data["FileData"] = self.FileData
            for k, v in kwargs.items():
                data[k] = v
            response = dev_client.put(path, data=json.dumps(data), timeout=None)
            return response.json()

    @staticmethod
    def search(FileName=None, FileKey=None, FileExtension=None, FileId=None):
        path = "/Files"
        params = {}
        if FileName:
            params["FileName"] = FileName
        if FileKey:
            params["FileKey"] = FileKey
        if FileExtension:
            params["FileExtension"] = FileExtension
        if FileId:
            params["FileId"] = FileId
        response = dev_client.get(path, params=params, timeout=60.0)
        return response.json()

    def get_shared_file_ids(self):
        return list(set([str(sf["SharedFileId"]) for sf in self.SharedFileIds]))

    def get_family_ids(self):
        return list(set([str(ff["FamilyId"]) for ff in self.FamilyFileIds]))

    def __repr__(self):
        return (
            f"File(FileId={self.FileId}, "
            f"FilePath={self.FilePath}, "
            f"FileName={self.FileName}, "
            f"FileKey={self.FileKey}, "
            f"Deleted={self.Deleted}, "
            f"FileData={self.FileData}, "
            f"FileLength={self.FileLength}, "
            f"Version={self.Version})"
        )


class FamilyType(FetchModel):
    """A class representing a family type"""

    def __init__(self, **kwargs):
        self.param_defaults = {
            "Name": None,
            "Parameters": None,
            "Files": None,
            "Id": None,
            "Sort": 0,
            "IsDefault": False,
            "Deleted": False,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return (
            f"FamilyType(Name={self.Name}, "
            f"Parameters={self.Parameters}, "
            f"Files={self.Files}, "
            f"Id={self.Id}, "
            f"Sort={self.Sort}, "
            f"IsDefault={self.IsDefault}, "
            f"Deleted={self.Deleted})"
        )

    @classmethod
    def from_dict(cls, data, **kwargs):
        """Create a new instance based on a JSON dict. Any kwargs should be
        supplied by the inherited, calling class.
        """

        json_data = data.copy()
        if kwargs:
            for key, val in kwargs.items():
                json_data[key] = val

        json_data["Parameters"] = json_class_parse(Parameter, "Parameters", json_data)
        json_data["Files"] = json_class_parse(File, "Files", json_data)

        c = cls(**json_data)
        c._json = data
        return c


class GroupedFamily(FetchModel):
    """A class representing a child family of a model group"""

    def __init__(self, **kwargs):
        self.param_defaults = {
            "ChildFamilyId": None,
            "FamilyTypeId": None,
            "ChildFamilyName": None,
            "InstanceCount": 1,
            "Parameters": None,
            "Sort": 0,
            "Width": None,
            "Depth": None,
            "Rotation": 0,
            "ChildModelGroups": None,
            "Deleted": False,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return (
            f"GroupedFamily(ChildFamilyName={self.ChildFamilyName}, "
            f"Parameters={self.Parameters}, "
            f"ChildFamilyId={self.ChildFamilyId}, "
            f"FamilyTypeId={self.FamilyTypeId}, "
            f"InstanceCount={self.InstanceCount}, "
            f"Sort={self.Sort}, "
            f"Width={self.Width}, "
            f"Depth={self.Depth}, "
            f"Rotation={self.Rotation}, "
            f"ChildModelGroups={self.ChildModelGroups}, "
            f"Deleted={self.Deleted})"
        )

    @classmethod
    def from_dict(cls, data, **kwargs):
        """Create a new instance based on a JSON dict. Any kwargs should be
        supplied by the inherited, calling class.
        """

        json_data = data.copy()
        if kwargs:
            for key, val in kwargs.items():
                json_data[key] = val

        json_data["Parameters"] = json_class_parse(Parameter, "Parameters", json_data)
        json_data["ChildModelGroups"] = json_class_parse(
            GroupedFamily, "ChildModelGroups", json_data
        )

        c = cls(**json_data)
        c._json = data
        return c


class Family(FetchModel):
    """A class representing a file of a family"""

    def __init__(self, **kwargs):
        self.param_defaults = {
            "Id": None,
            "Name": None,
            "CategoryName": None,
            "FamilyObjectType": None,
            "GroupedFamilies": None,
            "Files": None,
            "FamilyTypes": None,
            "Properties": None,
            "Parameters": None,
            "LoadMethod": 0,
            "Status": 2,
            "Deleted": False,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    @classmethod
    def from_id(cls, id: str):
        path = f"/Home/Family/{id}"
        response = client.get(path)
        fam_dict = response.json()["BusinessFamilies"][0]
        return Family.from_dict(fam_dict)

    def delete(self):
        path = f"/Family/{self.Id}"
        response = client.delete(path)
        return response.json()

    def restore(self):
        path = f"/Family/{self.Id}/Restore"
        response = client.post(path)
        return response.json()

    def update(self, data):
        path = f"/Family"
        data["FamilyId"] = self.Id
        response = client.patch(path, data=json.dumps(data))
        return response.json()

    def create(self):
        path = f"/v2/Family/"
        response = client.post(path, data=json.dumps(self.to_dict()))
        return response.json()

    @classmethod
    def from_dict(cls, data, **kwargs):
        """Create a new Family instance based on JSON dict."""

        json_data = data.copy()
        if kwargs:
            for key, val in kwargs.items():
                json_data[key] = val

        json_data["Properties"] = json_class_parse(Property, "Properties", json_data)
        json_data["Parameters"] = json_class_parse(Parameter, "Parameters", json_data)
        json_data["Files"] = json_class_parse(File, "Files", json_data)
        json_data["FamilyTypes"] = json_class_parse(
            FamilyType, "FamilyTypes", json_data
        )
        json_data["GroupedFamilies"] = json_class_parse(
            GroupedFamily, "GroupedFamilies", json_data
        )

        c = cls(**json_data)
        c._json = data
        return c

    @staticmethod
    def search(
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
        path = "/SharedFile/Families"
        data = {}
        data["FamilyObjectType"] = FamilyObjectType
        data["CategoryName"] = CategoryName
        data["ParameterName"] = ParameterName
        data["ParameterValue"] = ParameterValue
        data["ParameterValueMatchType"] = ParameterValueMatchType
        data["PropertyName"] = PropertyName
        data["PropertyValue"] = PropertyValue
        data["PropertyValueMatchType"] = PropertyValueMatchType
        data["FileKey"] = FileKey

        response = client.post(path, data=json.dumps(data), timeout=60.0)
        return response.json()

    def __repr__(self):
        return (
            f"Family(Name={self.Name}, "
            f"CategoryName={self.CategoryName}, "
            f"FamilyObjectType={self.FamilyObjectType}, "
            f"GroupedFamilies={self.GroupedFamilies}, "
            f"Parameters={self.Parameters}, "
            f"Files={self.Files}, "
            f"Id={self.Id}, "
            f"LoadMethod={self.LoadMethod}, "
            f"Status={self.Status}, "
            f"Deleted={self.Deleted})"
        )


class SharedAttribute(FetchModel):
    """A class representing a shared rule"""

    def __init__(self, **kwargs):
        self.param_defaults = {
            "SharedAttributeId": None,
            "AttributeType": 0,
            "Name": None,
            "Value": None,
            "DataType": None,
            "ParameterType": None,
            "Sort": None,
            "Hidden": None,
            "ParameterId": None,
            "Deleted": False,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return (
            f"SharedAttribute(SharedAttributeId={self.SharedAttributeId}, "
            f"AttributeType={self.AttributeType}, "
            f"Name={self.Name}, "
            f"Value={self.Value}, "
            f"DataType={self.DataType}, "
            f"ParameterType={self.ParameterType}, "
            f"Sort={self.Sort}, "
            f"Hidden={self.Hidden}, "
            f"ParameterId={self.ParameterId}, "
            f"Deleted={self.Deleted}"
        )


class SharedFile(FetchModel):
    """A class representing a shared rule"""

    def __init__(self, **kwargs):
        self.param_defaults = {
            "SharedFileId": None,
            "Description": None,
            "CategoryName": None,
            "FamilyObjectType": None,
            "ParameterName": None,
            "ParameterValue": None,
            "ParameterValueMatchType": None,
            "PropertyName": None,
            "PropertyValue": None,
            "PropertyValueMatchType": None,
            "FileKey": None,
            "Deleted": False,
            "Files": None,
            "Attributes": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return (
            f"SharedFile(SharedFileId={self.SharedFileId}, "
            f"Description={self.Description}, "
            f"CategoryName={self.CategoryName}, "
            f"FamilyObjectType={self.FamilyObjectType}, "
            f"ParameterName={self.ParameterName}, "
            f"ParameterValue={self.ParameterValue}, "
            f"ParameterValueMatchType={self.ParameterValueMatchType}, "
            f"PropertyName={self.PropertyName}, "
            f"PropertyValue={self.PropertyValue}, "
            f"PropertyValueMatchType={self.PropertyValueMatchType}, "
            f"FileKey={self.FileKey}, "
            f"Deleted={self.Deleted}, "
            f"Files={self.Files}, "
            f"Attributes={self.Attributes})"
        )

    @classmethod
    def from_id(cls, id):
        path = f"/SharedFile/{str(id)}"
        response = client.get(path, timeout=30.0)
        shared_dict = response.json()
        return SharedFile.from_dict(shared_dict)

    @classmethod
    def from_dict(cls, data, **kwargs):
        """Create a new Family instance based on JSON dict."""

        json_data = data.copy()
        if kwargs:
            for key, val in kwargs.items():
                json_data[key] = val

        json_data["Files"] = json_class_parse(File, "Files", json_data)
        # for _file in json_data["Files"]:
        #     _file.FileData = None
        json_data["Attributes"] = json_class_parse(
            SharedAttribute, "Attributes", json_data
        )

        c = cls(**json_data)
        c._json = data
        return c

    @staticmethod
    def get_shared_rules():
        path = f"/SharedFiles"
        response = client.get(path)
        return response.json().get("SharedFiles")

    def create(self):
        path = f"/SharedFile"
        # self.SharedFileId = None
        response = client.post(path, data=json.dumps(self.to_dict()))
        return response.json()

    def get_families(self):
        path = "/SharedFile/Families"
        data = {}
        data["FamilyObjectType"] = self.FamilyObjectType
        data["CategoryName"] = self.CategoryName
        data["ParameterName"] = self.ParameterName
        data["ParameterValue"] = self.ParameterValue
        data["ParameterValueMatchType"] = self.ParameterValueMatchType
        data["PropertyName"] = self.PropertyName
        data["PropertyValue"] = self.PropertyValue
        data["PropertyValueMatchType"] = self.PropertyValueMatchType
        data["FileKey"] = self.FileKey
        response = client.post(path, data=json.dumps(data), timeout=60.0)
        return response.json()

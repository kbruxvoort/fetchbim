from __future__ import annotations

import base64
import tkinter
import json

from enum import Enum
from typing import Optional
from tkinter import filedialog

from pydantic import BaseModel, Field

from . import client, dev_client


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


class Status(int, Enum):
    PUBLIC: int = 0
    PRIVATE: int = 1
    WIP: int = 2
    WEB: int = 3


class LoadMethod(int, Enum):
    STANDARD: int = 0
    DYNAMIC: int = 1


class ObjectType(str, Enum):
    FAMILY: str = "Family"
    GROUP: str = "ModelGroup"


class ParameterType(str, Enum):
    TYPE: str = "Type"
    INST: str = "Instance"


class AttributeType(int, Enum):
    PARAMETER: int = 0
    PROPERTY: int = 1


class DataType(str, Enum):
    TEXT: str = "Text"
    INTEGER: str = "Integer"
    NUMBER: str = "Number"
    LENGTH: str = "Length"
    AREA: str = "Area"
    VOLUME: str = "Volume"
    ANGLE: str = "Angle"
    SLOPE: str = "Slope"
    CURRENCY: str = "Currency"
    MASS: str = "MassDensity"
    URL: str = "URL"
    BOOLEAN: str = "Boolean"
    MULTITEXT: str = "MultlineText"


class MatchType(int, Enum):
    EQUALS: int = 0
    STARTS: int = 1
    ENDS: int = 2
    CONTAINS: int = 3


class FileKey(str, Enum):
    pass


class Parameter(BaseModel):
    id: int = Field(None, alias="ParameterId")
    name: str
    value: str
    parameter_type: ParameterType
    data_type: DataType
    sort: int = 0
    hidden: bool = False

    class Config:
        alias_generator = to_camel


class Property(BaseModel):
    id: int
    name: str
    value: str
    deleted: bool

    class Config:
        alias_generator = to_camel


class File(BaseModel):
    id: int = Field(None, alias="FileId")
    name: str = Field(None, alias="FileName")
    extension: str = Field(None, alias="FileExtension")
    deleted: bool = False
    key: Optional[str] = Field(None, alias="FileKey")
    data: Optional[str] = Field(None, alias="FileData", repr=False)
    path: Optional[str] = Field(None, alias="FilePath", repr=False)

    class Config:
        alias_generator = to_camel

    def file_from_path(self):
        try:
            with open(self.path, "rb") as file:
                byteform = base64.b64encode(file.read())
                self.data = byteform.decode("utf-8")
        except TypeError as e:
            print(f"File path is incorrect: {e}")

    @classmethod
    def pick_file(cls, file_key: str) -> File:
        """Returns a file object based on file selector dialog

        Args:
            file_key (str):
                File key represented as a string. File key designates how the
                file will be treated in app. Example: "FamilyRevitFile"

        Returns:
            File: File object based on local file.
        """
        root = tkinter.Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename()
        file_ext = file_path.split(".")[-1]
        file_name = file_path.split("/")[-1].split(".")[0]
        c = cls(
            FilePath=file_path,
            FileExtension=file_ext,
            FileName=file_name,
            FileKey=file_key,
            FileId=0,
            FileData=None,
        )
        c.file_from_path()
        return c

    @classmethod
    def from_id(cls, id: int) -> File:
        """Returns a new File instance based on the file id.

        Args:
            id (int): File Id.

        Returns:
            File: File object with corresponding id
        """
        path = "/Files"
        params = {"FileId": id}
        response = dev_client.get(path, params=params)
        file_dict = response.json()
        if isinstance(file_dict, list):
            try:
                file_dict = file_dict[0]
            except IndexError as e:
                print(f"No file found with FileId: {id}")
        return cls(**file_dict)

    def update(self):
        path = "/File"
        response = dev_client.patch(
            path, data=self.json(by_alias=True, include={"name", "key"})
        )
        return File(**response.json())

    def replace(self) -> dict:
        """Replaces file of given FileId with base64 FileData binary file.
        Optional parameters will default to existing values for given FileId.
        Updates any existing Family <-> File mappings.
        Updates any shared file references.

        Returns:
            dict: Response dictionary containing newly created file
        """
        path = f"/File/{self.id}"
        data = {}
        if self.data is None:
            self.file_from_path()
            if self.data:
                response = dev_client.put(
                    path, data=self.json(by_alias=True, exclude={"path"}), timeout=None
                )
                return response.json()

    @staticmethod
    def search(
        name: Optional[str] = None,
        key: Optional[str] = None,
        extension: Optional[str] = None,
        id: Optional[str] = None,
    ) -> list[File]:
        """Returns list of Files by searching database based on search criteria

        Args:
            name (Optional[str], optional): Name of file - Contains string. Defaults to None.
            key (Optional[str], optional): File key - Exact match. Defaults to None.
            extension (Optional[str], optional): File extension - Exact match. Defaults to None.
            id (Optional[str], optional): File id - Exact match. Defaults to None.

        Returns:
            list[File]: List of File objects
        """
        path = "/Files"
        params = {}
        if name:
            params["FileName"] = name
        if key:
            params["FileKey"] = key
        if extension:
            params["FileExtension"] = extension
        if id:
            params["FileId"] = id
        response = dev_client.get(path, params=params, timeout=60.0)
        return [File(**_file) for _file in response.json()]

    def attach_to_families(self, family_ids: list[str]):
        path = "/FamilyFiles"
        data = [{"FamilyId": family_id, "FileId": self.id} for family_id in family_ids]
        response = dev_client.post(path, json=data)
        return response.json()


class FamilyType(BaseModel):
    id: str
    name: str
    is_default: bool = False
    sort: int = 0
    deleted: bool = False
    files: Optional[list[File]]
    parameters: Optional[list[Parameter]]

    class Config:
        alias_generator = to_camel


class GroupedFamily(BaseModel):
    id: str = Field(None, alias="ChildFamilyId")
    type_id: str = Field(None, alias="FamilyTypeId")
    count: int = Field(1, alias="InstanceCount")
    sort: int = 0
    width: Optional[float] = 0
    depth: Optional[float] = 0
    rotation: Optional[float] = 0
    deleted: bool = False
    parameters: Optional[list[Parameter]]
    family_name: Optional[str] = Field(None, alias="ChildFamilyName")
    hosted_families: Optional[list[GroupedFamily]] = Field(
        default_factory=list, alias="ChildModelGroups"
    )

    class Config:
        alias_generator = to_camel


class Family(BaseModel):
    id: str
    name: str
    category_name: str
    family_object_type: ObjectType
    load_method: LoadMethod
    status: Status
    deleted: bool
    grouped_families: Optional[list[GroupedFamily]]
    files: Optional[list[File]]
    family_types: Optional[list[FamilyType]]
    properties: Optional[list[Property]]
    parameters: Optional[list[Parameter]]

    class Config:
        alias_generator = to_camel

    @classmethod
    def from_id(cls, id: str):
        path = f"/Home/Family/{id}"
        response = client.get(path)
        fam_dict = response.json()["BusinessFamilies"][0]
        return cls(**fam_dict)

    def create(self):
        path = f"/v2/Family/"
        response = client.post(path, data=self.json(by_alias=True))
        return response.json()

    def update(self, **kwargs):
        path = f"/Family"
        data = {}
        data["FamilyId"] = self.id
        for k, v in kwargs.items():
            data[k] = v
        response = client.patch(path, data=json.dumps(data))
        return response.json()

    def delete(self):
        path = f"/Family/{self.id}"
        response = client.delete(path)
        return response.json()

    @staticmethod
    def restore(id):
        path = f"/Family/{id}/Restore"
        response = client.post(path)
        return response.json()

    @staticmethod
    def search(
        family_object_type=None,
        category_name=None,
        parameter_name=None,
        parameter_value=None,
        parameter_match_type=None,
        property_name=None,
        property_value=None,
        property_match_type=None,
        file_key=None,
    ):
        path = "/SharedFile/Families"
        data = {}
        data["FamilyObjectType"] = family_object_type
        data["CategoryName"] = category_name
        data["ParameterName"] = parameter_name
        data["ParameterValue"] = parameter_value
        data["ParameterValueMatchType"] = parameter_match_type
        data["PropertyName"] = property_name
        data["PropertyValue"] = property_value
        data["PropertyValueMatchType"] = property_match_type
        data["FileKey"] = file_key

        response = client.post(path, json=data, timeout=60.0)
        families = response.json()
        return [Family(**fam) for fam in families]


class SharedAttribute(BaseModel):
    id: int = Field(None, alias="SharedAttributeId")
    name: str
    value: str
    attribute_type: AttributeType
    sort: int
    hidden: bool = False
    deleted: bool = False
    parameter_type: Optional[ParameterType]
    data_Type: Optional[DataType]

    class Config:
        alias_generator = to_camel


class SharedRule(BaseModel):
    id: int = Field(None, alias="SharedFileId")
    name: str = Field(None, alias="Description")
    category_name: str
    family_object_type: ObjectType
    deleted: bool = False
    parameter_name: Optional[str]
    parameter_value: Optional[str]
    parameter_match_type: Optional[MatchType] = Field(
        None, alias="ParameterValueMatchType"
    )
    property_name: Optional[str]
    property_value: Optional[str]
    property_match_type: Optional[MatchType] = Field(
        None, alias="ParameterValueMatchType"
    )
    file_key: Optional[str]
    files: Optional[list[File]]
    attributes: Optional[list[SharedAttribute]]
    families: Optional[list[Family]]

    class Config:
        alias_generator = to_camel

    @classmethod
    def from_id(cls, id):
        path = f"/SharedFile/{str(id)}"
        response = client.get(path, timeout=30.0)
        shared_dict = response.json()
        return cls(**shared_dict)

    def get_families(self):
        path = "/SharedFile/Families"
        data = self.json(
            by_alias=True,
            exclude={"name", "deleted", "files", "attributes", "families"},
        )
        response = client.post(path, json=data, timeout=60.0)
        return [Family(**fam) for fam in response.json()]

    @staticmethod
    def get_shared_rules():
        path = f"/SharedFiles"
        response = client.get(path)
        rules = response.json().get("SharedFiles")
        return [SharedRule(**rule) for rule in rules]

    def create(self):
        path = f"/SharedFile"
        response = client.post(
            path, json=self.json(by_alias=True, exclude={"families"})
        )
        return response.json()

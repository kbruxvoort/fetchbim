from __future__ import annotations

import base64
import tkinter
import json

from enum import Enum, IntEnum
from typing import Optional
from tkinter import filedialog

from pydantic import BaseModel, Field

from . import client, dev_client


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


class Status(IntEnum):
    PUBLIC = 0
    PRIVATE = 1
    WIP = 2
    WEB = 3


class LoadMethod(IntEnum):
    STANDARD = 0
    DYNAMIC = 1


class ObjectType(str, Enum):
    FAMILY = "Family"
    GROUP = "ModelGroup"
    SCHEDULE = "Schedule"
    TEMPLATE = "Template"

    def __str__(self):
        return self.value


class ParameterType(str, Enum):
    TYPE = "Type"
    INST = "Instance"

    def __str__(self):
        return self.value


class AttributeType(IntEnum):
    PARAMETER = 0
    PROPERTY = 1


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


class MatchType(IntEnum):
    EQUALS = 0
    STARTS = 1
    ENDS = 2
    CONTAINS = 3


class FileKey(str, Enum):
    REVIT = "FamilyRevitFile"
    REVIT_15 = "FamilyRevitFile2015"
    REVIT_16 = "FamilyRevitFile2016"
    REVIT_17 = "FamilyRevitFile2017"
    REVIT_18 = "FamilyRevitFile2018"
    REVIT_19 = "FamilyRevitFile2019"
    REVIT_20 = "FamilyRevitFile2020"
    REVIT_21 = "FamilyRevitFile2021"
    REVIT_22 = "FamilyRevitFile2022"
    IMAGE_LG = "FamilyImageLarge"
    IMAGE_MD = "FamilyImageMedium"
    IMAGE_SM = "FamilyImageSmall"
    RENDER_LG = "FamilyRenderingLarge"
    RENDER_MD = "FamilyRenderingMedium"
    RENDER_SM = "FamilyRenderingSmall"
    CSI_SPEC = "DOC-CSISpec"
    WARRANTY = "PDF-Warranty"
    SUSTAIN = "PDF-Sustainability"
    SPEC_MANUAL = "PDF-SpecManual"
    FINISHES = "PDF-FinishOptions"
    DRAWING = "PDF-Drawing"
    GENERIC_1 = "PDF-Generic1"
    GENERIC_2 = "PDF-Generic2"
    GENERIC_3 = "PDF-Generic3"
    GENERIC_4 = "PDF-Generic4"
    GENERIC_5 = "PDF-Generic5"
    MATERIAL = "MaterialLibrary"
    GALLERY_1 = "FamilyGalleryLarge1"
    GALLERY_2 = "FamilyGalleryLarge2"
    GALLERY_3 = "FamilyGalleryLarge3"
    GALLERY_4 = "FamilyGalleryLarge4"
    GALLERY_5 = "FamilyGalleryLarge5"
    GALLERY_6 = "FamilyGalleryLarge6"
    GALLERY_7 = "FamilyGalleryLarge7"
    GALLERY_8 = "FamilyGalleryLarge8"
    GALLERY_9 = "FamilyGalleryLarge9"
    GALLERY_10 = "FamilyGalleryLarge10"
    GALLERY_11 = "FamilyGalleryLarge11"
    GALLERY_12 = "FamilyGalleryLarge12"
    GALLERY_13 = "FamilyGalleryLarge13"
    GALLERY_14 = "FamilyGalleryLarge14"
    GALLERY_15 = "FamilyGalleryLarge15"

    def __str__(self):
        return self.value


class Parameter(BaseModel):
    id: Optional[int] = Field(None, alias="ParameterId")
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


class File(BaseModel):
    id: int = Field(default=None, alias="FileId")
    name: str = Field(None, alias="FileName")
    extension: str = Field(None, alias="FileExtension")
    deleted: bool = False
    key: Optional[str] = Field(
        None,
        alias="FileKey",
    )
    data: Optional[str] = Field(None, alias="FileData", repr=False)
    path: Optional[str] = Field(None, alias="FilePath", repr=False)

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True

    def file_from_path(self) -> None:
        try:
            with open(self.path, "rb") as file:
                byteform = base64.b64encode(file.read())
                self.data = byteform.decode("utf-8")
        except TypeError as e:
            print(f"File path is incorrect: {e}")

    @classmethod
    def pick_file(cls, key: str) -> File:
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
            FileKey=key,
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

    def update(self) -> dict:
        path = "/File"
        response = dev_client.patch(
            path, data=self.json(by_alias=True, include={"name", "key"})
        )
        return response.json()

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
            if self.path:
                self.file_from_path()
            else:
                self.pick_file(self.key)
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

    def attach_to_families(self, family_ids: list[str]) -> dict:
        path = "/FamilyFiles"
        data = [{"FamilyId": family_id, "FileId": self.id} for family_id in family_ids]
        response = dev_client.post(path, json=data)
        return response.json()


class FamilyType(BaseModel):
    id: Optional[str] = None
    name: str
    is_default: Optional[bool] = False
    deleted: bool = False
    files: Optional[list[File]]
    parameters: Optional[list[Parameter]]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True


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
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True


class Family(BaseModel):
    id: Optional[str] = None
    name: str
    category_name: str
    family_object_type: ObjectType = ObjectType.FAMILY
    load_method: LoadMethod = LoadMethod.STANDARD
    status: Status = Status.WIP
    deleted: bool = False
    grouped_families: Optional[list[GroupedFamily]] = None
    files: Optional[list[File]] = None
    family_types: Optional[list[FamilyType]] = None
    properties: Optional[list[Property]] = None
    parameters: Optional[list[Parameter]] = None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True

    @classmethod
    def from_id(cls, id: str) -> Family:
        path = f"/Home/Family/{id}"
        response = client.get(path)
        fam_dict = response.json()["BusinessFamilies"][0]
        return cls(**fam_dict)

    def create(self) -> dict:
        path = f"/v2/Family/"
        response = client.post(path, data=self.json(by_alias=True))
        return response.json()

    def update(self, **kwargs) -> dict:
        path = f"/Family"
        data = {}
        data["FamilyId"] = self.id
        for k, v in kwargs.items():
            data[k] = v
        response = client.patch(path, data=json.dumps(data))
        return response.json()

    def delete(self) -> dict:
        path = f"/Family/{self.id}"
        response = client.delete(path)
        return response.json()

    @staticmethod
    def restore(id: str) -> dict:
        path = f"/Family/{id}/Restore"
        response = client.post(path)
        return response.json()

    @staticmethod
    def search(
        family_object_type: Optional[ObjectType] = None,
        category_name: Optional[str] = None,
        parameter_name: Optional[str] = None,
        parameter_value: Optional[str] = None,
        parameter_match_type: Optional[MatchType] = None,
        property_name: Optional[str] = None,
        property_value: Optional[str] = None,
        property_match_type: Optional[MatchType] = None,
        file_key: Optional[str] = None,
    ) -> list[Family]:
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
    id: Optional[int] = Field(0, alias="SharedAttributeId")
    name: str
    value: str
    attribute_type: AttributeType
    sort: int = 0
    hidden: bool = False
    deleted: bool = False
    parameter_type: Optional[ParameterType]
    data_Type: Optional[DataType]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True


class SharedRule(BaseModel):
    id: Optional[int] = Field(0, alias="SharedFileId")
    name: str = Field(None, alias="Description")
    category_name: Optional[str] = ""
    family_object_type: Optional[ObjectType] = None
    deleted: bool = False
    parameter_name: Optional[str] = None
    parameter_value: Optional[str] = None
    parameter_match_type: Optional[MatchType] = Field(
        None, alias="ParameterValueMatchType"
    )
    property_name: Optional[str] = None
    property_value: Optional[str] = None
    property_match_type: Optional[MatchType] = Field(
        default=None, alias="PropertyValueMatchType"
    )
    file_key: Optional[str] = None
    files: Optional[list[File]] = None
    attributes: Optional[list[SharedAttribute]] = None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True

    @classmethod
    def from_id(cls, id: int) -> SharedRule:
        path = f"/SharedFile/{id}"
        response = client.get(path, timeout=30.0)
        shared_dict = response.json()
        return cls(**shared_dict)

    def get_families(self) -> list[Family]:
        path = "/SharedFile/Families"
        data = self.json(
            by_alias=True,
            exclude={"name", "deleted", "files", "attributes", "families"},
        )
        response = client.post(path, data=data, timeout=60.0)
        return [Family(**fam) for fam in response.json()]

    @staticmethod
    def get_shared_rules() -> list[SharedRule]:
        path = f"/SharedFiles"
        response = client.get(path, timeout=None)
        rules = response.json().get("SharedFiles")
        if rules:
            return [SharedRule(**rule) for rule in rules]

    def create(self) -> dict:
        path = f"/SharedFile"
        response = client.post(
            path, data=self.json(by_alias=True, exclude={"families"})
        )
        return response.json()

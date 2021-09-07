import base64
import json
from enum import Enum


class AttributeType(Enum):
    PARAMETER = 0
    PROPERTY = 1
    FILE = 2


class Attribute(object):
    def __init__(self, Name, Value, Deleted=False):
        self.Name = Name
        self.Value = Value
        self.Deleted = Deleted
        super(Attribute, self).__init__()

    def to_json(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return "{}: {}".format(self.Name, self.Value)


class Property(Attribute):
    AttributeType = 1

    def __init__(self, Name, Value, Deleted=False, Id=0):
        super(Property, self).__init__(Name, Value, Deleted)
        self.Id = Id
        # self.AttributeType = 1

    @classmethod
    def from_json(cls, json_dict):
        return cls(
            json_dict.get("Name", ""),
            json_dict.get("Value", ""),
            json_dict.get("Deleted", False),
        )

    def __repr__(self):
        return "Property(Name={}, Value={}, Deleted={}, Id={})".format(self.Name, self.Value, self.Deleted, self.Id)


class Parameter(Attribute):
    AttributeType = 0

    def __init__(
        self,
        Name,
        Value,
        Deleted=False,
        DataType="Text",
        ParameterType="Type",
        Sort=0,
        Hidden=False,
        ParameterId=0,
    ):
        super(Parameter, self).__init__(Name, Value, Deleted)
        self.DataType = DataType
        self.ParameterType = ParameterType
        self.Sort = Sort
        self.Hidden = Hidden
        # self.AttributeType = 0
        self.ParameterId = ParameterId

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

        return cls(Name, Value, Deleted, DataType, ParameterType, Sort, Hidden, ParameterId)

    def __repr__(self):
        return "Parameter(Name={}, Value={}, Deleted={}, DataType={}, ParameterType={}, Sort={}, Hidden={}, ParameterId={})".format(
            self.Name,
            self.Value,
            self.Deleted,
            self.DataType,
            self.ParameterType,
            self.Sort,
            self.Hidden,
            self.ParameterId,
        )


class File(Attribute):
    def __init__(self, FilePath, FileKey="FamilyRevitFile", Deleted=False, FileData="", FileLength=0, Version=""):
        super(File, self).__init__(FileKey, FilePath, Deleted)
        self.FilePath = FilePath
        self.FileKey = FileKey
        self.FileName = FilePath.split("\\")[-1].split(".")[0]
        self.FileExtension = "." + FilePath.split(".")[1]
        self.FileNameWithExtension = self.FileName + self.FileExtension
        self.FileLength = FileLength
        self.Version = Version

        if FileData == "":
            with open(self.FilePath, "rb") as file:
                byteform = base64.b64encode(file.read())
                self.FileData = byteform.decode("utf-8")
        else:
            self.FileData = FileData

    def length_to_kb(self):
        return int(self.FileLength / 1024)

    @classmethod
    def from_json(cls, json_dict):
        FilePath = json_dict.get("FileNameWithExtension", "")
        FileKey = json_dict.get("FileKey", "")
        Deleted = json_dict.get("Deleted", False)
        FileData = json_dict.get("FileData", "")
        FileLength = json_dict.get("FileLength", 0)
        Version = json_dict.get("Version", "")

        return cls(FilePath, FileKey, Deleted, FileData, FileLength, Version)

    def __repr__(self):
        return "File(FilePath={}, FileKey={}, Deleted={}, FileData={}, FileLength={}, Version={})".format(
            self.FilePath, self.FileKey, self.Deleted, self.FileData, self.FileLength, self.Version
        )

    def __str__(self):
        return "{}: {}".format(self.FileKey, self.FileNameWithExtension)

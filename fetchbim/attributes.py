import base64
import json
from enum import Enum

class AttributeType(Enum):
    PROPERTY = 0
    PARAMETER = 1
    FILE = 2


class Attribute(object):
    def __init__(self, Name, Value, Deleted=False):
        self.Name = Name
        self.Value = Value
        self.Deleted = Deleted
        super(Attribute, self).__init__()

    def to_json(self):
        return json.dumps(self.__dict__)




class Property(Attribute):
    def __init__(self, Name, Value, Deleted=False, Id=0):
        super().__init__(Name, Value, Deleted)
        self.Id = Id
        self.AttributeType = 0

    @classmethod
    def from_json(cls, json_dict, **kwargs):
        prop = cls(json_dict.get('Name', ""), json_dict.get('Value', ""), json_dict.get('Deleted', False))
        prop.Id = json_dict.get('Id', 0)
        for k,v in kwargs.items():
            prop[k] = v
        return prop

    def __repr__(self):
        return 'Property(Name={}, Value={}, Deleted={}, Id={})'.format(self.Name, self.Value, self.Deleted, self.Id)

    def __str__(self):
        return '{}: {}'.format(self.Name, self.Value)


class Parameter(Attribute):
    def __init__(self, Name, Value, Deleted=False, DataType='Text', ParameterType='Type', Sort=0, Hidden=False, ParameterId=0):
        super(Parameter, self).__init__(Name, Value, Deleted)
        self.DataType = DataType
        self.ParameterType = ParameterType
        self.Sort = Sort
        self.Hidden = Hidden
        self.AttributeType = 1
        self.ParameterId = ParameterId
        # self.Modified = False
        # self.OldValue = None
        # self.IsFormula = None
        # self.IsCalculated = False
        # self.CalculatedFormula = ""
        # self.CalculatedValue = None

    @classmethod
    def from_json(cls, json_dict, **kwargs):
        Name = json_dict.get('Name', "")
        Value = json_dict.get('Value', "")
        Deleted = json_dict.get('Deleted', False)
        DataType = json_dict.get('DataType')
        ParameterType = json_dict.get('ParameterType')
        Sort = json_dict.get('Sort')
        Hidden = json_dict.get('Hidden', False)
        ParameterId = json_dict.get('ParameterId', 0)
        
        param =  cls(Name, Value, Deleted, DataType, ParameterType, Sort, Hidden, ParameterId)
        for k,v in kwargs.items():
            param[k] = v

        return param

    def __repr__(self):
        return 'Parameter(Name={}, Value={}, Deleted={}, DataType={}, ParameterType={}, Sort={}, Hidden={}, ParameterId={})'.format(self.Name, self.Value, self.Deleted, self.DataType, self.ParameterType, self.Sort, self.Hidden, self.ParameterId)

    def __str__(self):
        return '{}: {}'.format(self.Name, self.Value)


class File(Attribute):
    def __init__(self, FilePath, FileKey='FamilyRevitFile', Deleted=False, FileData=""):
        super(Attribute, self).__init__(FileKey, FilePath, Deleted)
        self.FilePath = FilePath
        self.FileKey = FileKey
        self.FileName = FilePath.split("\\")[-1].split(".")[0]
        self.FileExtension = "."+FilePath.split(".")[1]
        self.FileNameWithExtension = self.FileName + self.FileExtension

    # def b64_encode(self):
        if FileData == "":
            with open(self.FilePath, 'rb') as file:
                byteform = base64.b64encode(file.read())
                self.FileData = byteform.decode("utf-8")
        else:
            self.FileData = FileData

    @classmethod
    def from_json(cls, json_dict, **kwargs):
        FilePath = json_dict.get('FileNameWithExtension', "")
        FileKey = json_dict.get('FileKey', "")
        Deleted = json_dict.get('Deleted', False)
        FileData = json_dict.get('FileData', "")

        file = cls(FilePath, FileKey, Deleted, FileData)
        for k,v in kwargs.items():
            file[k] = v

        return file

    def __repr__(self):
        return 'File(FilePath={}, FileKey={}, Deleted={}, FileData={})'.format(self.FilePath, self.FileKey, self.Deleted, self.FileData)

    def __str__(self):
        return '{}: {}'.format(self.FileKey, self.FileNameWithExtension)
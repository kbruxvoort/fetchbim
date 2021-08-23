import requests
import settings
import json

from attributes import AttributeType, Property, Parameter, File
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
                print('{} is already in the family').format(param.Name)

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
            if f.FileName not in [x.FileName for x in self.Files]:
                self.Files.append(f)
            else:
                print('{} is already in the family').format(f.Name)

class FamilyType(Object):
    def __init__(self, Name, Parameters=None, Files=None, IsDefault=False, Deleted=False, Id=None, FamilyId=None):
        super(FamilyType, self).__init__(Name, Parameters)
        if Files == None:
            self.Files = []
        else:
            self.Files = Files
        self.IsDefault = IsDefault
        self.Deleted = Deleted
        if Id == None:
            self.Id = ""
        else:
            self.Id = Id
        if FamilyId == None:
            self.FamilyId = ""
        else:
            self.FamilyId = FamilyId

    @classmethod
    def from_json(cls, json_dict, **kwargs):
        ft = cls(json_dict.get('Name', ""), json_dict.get('Parameters', []), json_dict.get('Files', []), json_dict.get('IsDefault', False), json_dict.get('Deleted', False), json_dict.get('Id', ""), json_dict.get('FamilyId', ''))

        for k,v in kwargs.items():
            ft[k] = v
        
        return ft
    
    def add_attributes(self, attributes):
        if not isinstance(attributes, list):
            attributes = [attributes]
        for attribute in attributes:
            if attribute.__class__.__name__ == 'Parameter' and attribute.ParameterId not in [x.ParameterId for x in self.Parameters]:
                self.Parameters.append(attribute)
            elif attribute.__class__.__name__ == 'File' and attribute.FileId not in [x.FileId for x in self.Files]:
                self.Files.append(attribute)

    def __repr__(self):
        return 'FamilyType(Name={}, Parameters={}, Files={}, IsDefault={}, Deleted={}, Id={}, FamilyId={})'.format(self.Name, self.Parameters, self.Files, self.IsDefault, self.Deleted, self.Id, self.FamilyId)

    def __str__(self):
        return '[{}: {}]'.format(self.Id, self.Name)


class Family(Object):
    def __init__(self, Name, Status=Status.WIP.value, LoadMethod=0, CategoryName='None', FamilyObjectType='Family', Properties=None, Parameters=None, Files=None, Deleted=False, Id=None, GroupedFamilies=None, FamilyTypes=None):
        super(Family, self).__init__(Name, Parameters)
        self.Status = Status
        self.FamilyObjectType = FamilyObjectType
        self.CategoryName = CategoryName
        self.LoadMethod = LoadMethod
        self.Deleted = Deleted
        if Id == None:
            self.Id = ""
            self.IsNew = True
        else:
            self.Id = Id
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
    
    def post(self, **kwargs):
        data = self.to_json()
        response = requests.post(settings.POST_FAMILY_URL, data=data, headers=settings.DEV_HEADERS)
        if response.status_code in range(200, 299):
            result = response.json()
            self.Id = result.get('Id', "")
            self.Name = result.get('Name', "")
            self.Status = result.get('Status')
            self.LoadMethod = result.get('LoadMethod')
            self.CategoryName = result.get('CategoryName', "")
            self.FamilyObjectType = result.get('FamilyObjectType')
            self.Properties = []
            for prop in result.get('Properties', []):
                self.add_properties(Property.from_json(prop))
            self.Parameters = []
            for param in result.get('Parameters', []):
                self.add_parameters(Parameter.from_json(param))
            self.Files = []
            for file in result.get('Files', []):
                self.add_files(File.from_json(file))
            self.GroupedFamilies = []
            for fam in result.get('GroupedFamilies', []):
                self.GroupedFamilies.append(Family.from_json(fam))
            self.FamilyTypes, Type_Params = [], []
            for ft in result.get('FamilyTypes', []):
                for type_param in ft.get('Parameters'):
                    Type_Params.append(Parameter.from_json(type_param))
                ft['Parameters'] = Type_Params
                self.add_type(FamilyType.from_json(ft))
            self.Deleted = result.get('Deleted')
            for k,v in kwargs.items():
                self[k] = v

        else:
            print(response.text)

    def delete(self):
        self.is_deleted = True
        return requests.delete(settings.POST_FAMILY_URL + self.id, headers=settings.DEV_HEADERS)

    def restore(self):
        return requests.post(settings.POST_FAMILY_URL + self.id + "/Restore", headers=settings.DEV_HEADERS)

    @staticmethod
    def get_json(guid):
        response = requests.get(settings.GET_FAMILY + guid, headers=settings.DEV_HEADERS)
        if response.status_code in range(200, 299):
            try:
                return response.json()['BusinessFamilies'][0]
            except IndexError as e:
                print(e)


    @classmethod
    def from_json(cls, json_dict, **kwargs):
        Id = json_dict.get('Id', "")
        Name = json_dict.get('Name', "")
        Status = json_dict.get('Status')
        LoadMethod = json_dict.get('LoadMethod')
        CategoryName = json_dict.get('CategoryName', "")
        FamilyObjectType = json_dict.get('FamilyObjectType')
        Properties = []
        for prop in json_dict.get('Properties', []):
            Properties.append(Property.from_json(prop))
        # self.Properties = result.get('Properties')
        Parameters = []
        for param in json_dict.get('Parameters', []):
            Parameters.append(Parameter.from_json(param))
        # self.Parameters = result.get('Parameters')
        Files = []
        for file in json_dict.get('Files', []):
            Files.append(File.from_json(file))
        # self.Files = result.get('Files')
        Deleted = json_dict.get('Deleted')
        GroupedFamilies = []
        for fam in json_dict.get("GroupedFamilies", []):
            GroupedFamilies.append(Family.from_json(fam))
        FamilyTypes = []
        for fam_type in json_dict.get('FamilyTypes', []):
            FamilyTypes.append(FamilyType.from_json(fam_type))

        family = cls(Name, Status, LoadMethod, CategoryName, FamilyObjectType, Properties, Parameters, Files, Deleted, Id, GroupedFamilies, FamilyTypes)

        for k,v in kwargs.items():
            family[k] = v
        
        return family

    def add_type(self, fam_type):
        names = [ftype.Name for ftype in self.FamilyTypes]
        if fam_type.Name not in names:
            fam_type.FamilyId = self.Id
            self.FamilyTypes.append(fam_type)
        else:
            print('{} already exists in family').format(fam_type.Name)
        
    def get_property(self, name):
        prop = [x for x in self.Properties if x.Name == name]
        if len(prop) == 1:
            return prop[0]
        else:
            return prop

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
                print('{} is already in the family').format(prop.Name)
    
    def __repr__(self):
        return 'Family(Name={}, Status={}, LoadMethod={}, CategoryName={}, FamilyObjectType={}, Properties={}, Parameters={}, Files={}, Deleted={}, Id={}, GroupedFamilies={}, FamilyTypes={})'.format(self.Name, self.Status, self.LoadMethod, self.CategoryName, self.FamilyObjectType, self.Properties, self.Parameters, self.Files, self.Deleted, self.Id, self.GroupedFamilies, self.FamilyTypes)

    def __str__(self):
        return '[{}]: {}'.format(self.Id, self.Name)

class GroupedFamily:
    def __init__(self, ChildFamilyId, FamilyTypeId, ChildFamilyName="", InstanceCount=1, Deleted=False, Sort=0, Width=0, Depth=0, Rotation=0, Parameters=None):
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

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    @classmethod
    def from_json(cls, json_dict, **kwargs):
        ChildFamilyId = json_dict.get('ChildFamilyId')
        FamilyTypeId = json_dict.get('FamilyTypeId')
        ChildFamilyName = json_dict.get('ChildFamilyId')
        InstanceCount = json_dict.get('InstanceCount', 1)
        Deleted = json_dict.get('Deleted', False)
        Sort = json_dict.get('Sort', 0)
        Width = json_dict.get('Width', 0)
        Depth = json_dict.get('Depth', 0)
        Rotation = json_dict.get('Rotation', 0)
        Parameters = json_dict.get('Parameters', [])

        grouped_fam = cls(ChildFamilyId, FamilyTypeId, ChildFamilyName, InstanceCount, Deleted, Sort, Width, Depth, Rotation, Parameters)

        for k,v in kwargs.items():
            grouped_fam[k] = v

        return grouped_fam

    def __repr__(self):
        return 'GroupedFamily(ChildFamilyId={}, FamilyTypeId={}, Name={}, InstanceCount={}, Deleted={}, Sort={}, Width={}, Depth={}, Rotation={}, Parameters={})'.format(self.ChildFamilyId, self.FamilyTypeId, self.Name, self.InstanceCount, self.Deleted, self.Sort, self.Width, self.Depth, self.Rotation, self.Parameters)
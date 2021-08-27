import settings
import requests
import json

from family import Family
from notion import Property, Page
from attributes import Parameter, File
from enum import Enum

class MatchType(Enum):
    EQUALS = 0
    STARTS = 1
    ENDS = 2
    CONTAINS = 3



class Filter:
    def __init__(self, FamilyObjectType=None, CategoryName=None, ParameterName=None, ParameterValue=None, ParameterValueMatchType=None, PropertyName=None, PropertyValue=None, PropertyValueMatchType=None, FileKey=None):
  
        self.FamilyObjectType = FamilyObjectType
        self.CategoryName = CategoryName
        self.ParameterName = ParameterName
        self.ParameterValue = ParameterValue
        self.ParameterValueMatchType = ParameterValueMatchType
        self.PropertyName = PropertyName
        self.PropertyValue = PropertyValue
        self.PropertyValueMatchType = PropertyValueMatchType
        self.FileKey = FileKey

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


    def query(self):
        response = requests.post(settings.QUERY_FAMILIES, data=self.to_json(), headers=settings.BIM_HEADERS)
        return response.json()

    def get_ids(self):
        id_list = []
        families = self.query()
        for fam in families:
            id_list.append(fam['Id'])
        return id_list

    def __repr__(self):
        return 'SharedFile(Description={}, FamilyObjectType={}, CategoryName={}, ParameterName={}, ParameterValue={}, ParameterValueMatchType={}, PropertyName={}, PropertyValue={}, PropertyValueMatchType={}, FileKey={})'.format(self.Description, self.FamilyObjectType, self.CategoryName, self.ParameterName, self.ParameterValue, self.ParameterValueMatchType, self.PropertyName, self.PropertyValue, self.PropertyValueMatchType, self.FileKey)
        
    @staticmethod
    def delete_parameter_by_name(id_list, name_list):
        if not isinstance(name_list, list):
            name_list = [name_list]
        if not isinstance(id_list, list):
            id_list = [id_list]
        for _id in id_list:
            response = Family.get_json(_id)
            parameters = response['Parameters']
            for param in parameters:
                if param['Name'] in name_list:
                    param['Deleted'] = True
            requests.post(settings.POST_FAMILY, data=json.dumps(response), headers=settings.BIM_HEADERS)

class SharedFile(Filter):
    def __init__(self, Description, FamilyObjectType=None, CategoryName="", ParameterName=None, ParameterValue=None, ParameterValueMatchType=None, PropertyName=None, PropertyValue=None, PropertyValueMatchType=None, FileKey=None, Deleted=False, SharedFileId=None, Files=None, Attributes=None):
        super().__init__(FamilyObjectType, CategoryName, ParameterName, ParameterValue, ParameterValueMatchType, PropertyName, PropertyValue, PropertyValueMatchType, FileKey)
        self.Description = Description
        self.Deleted = Deleted
        if SharedFileId == None:
            self.SharedFileId = 0
        else:
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

    def post(self, **kwargs):
        data = self.to_json()
        response = requests.post(settings.GET_SHARED_FILE, data=data, headers=settings.BIM_HEADERS)
        if response.status_code in range(200, 299):
            results = response.json()

            self.Description = results.get('Description', "")
            self.FamilyObjectType = results.get('FamilyObjectType')
            self.CategoryName = results.get('CategoryName', "")
            self.ParameterName = results.get('ParameterName')
            self.ParameterValue = results.get('ParameterValue')
            self.ParameterValueMatchType = results.get('ParameterValueMatchType')
            self.PropertyName = results.get('PropertyName')
            self.PropertyValue = results.get('PropertyValue')
            self.PropertyValueMatchType = results.get('PropertyValueMatchType')
            self.FileKey = results.get('FileKey')
            self.Deleted = results.get('Deleted', False)
            self.SharedFileId = results.get('SharedFileId', 0)
            self.Files = []
            for file in results.get('Files', []):
                self.Files.append(File.from_json(file))
            for attr in self.Attributes:
                for attribute in results.get('Attributes', []):
                    if attr.Name == attribute['Name']:
                        attr.SharedAttributeId = attribute['SharedAttributeId']

            for k,v in kwargs.items():
                self[k] = v
        else:
            print(response.text)
        return response
    

    @staticmethod
    def get_all():
        response = requests.get(settings.ALL_SHARED_FILES, headers=settings.BIM_HEADERS)
        if response.status_code in range(200, 299):
            return response.json() 

    @classmethod
    def get_json(cls, SharedFileId):
        response = requests.get(settings.GET_SHARED_FILE + str(SharedFileId), headers=settings.BIM_HEADERS)
        if response.status_code in range(200, 299):
            return response.json()
        
    @classmethod
    def from_json(cls, SharedFileId, **kwargs):
        result = cls.get_json(str(SharedFileId))
        Description = result.get('Description', "")
        FamilyObjectType = result.get('FamilyObjectType')
        CategoryName = result.get('CategoryName')
        ParameterName = result.get('ParameterName')
        ParameterValue = result.get('ParameterValue')
        ParameterValueMatchType = result.get('ParameterValueMatchType')
        PropertyName = result.get('PropertyName')
        PropertyValue = result.get('PropertyValue')
        PropertyValueMatchType = result.get('PropertyValueMatchType')
        FileKey = result.get('FileKey')
        Deleted = result.get('Deleted')
        SharedFileId = result.get('SharedFileId')
        Files = result.get('Files')
        Attributes = []
        for attribute in result.get('Attributes'):
            Attributes.append(SharedAttribute.from_json(attribute))

        shared_file = cls(Description, FamilyObjectType, CategoryName, ParameterName, ParameterValue, ParameterValueMatchType, PropertyName, PropertyValue, PropertyValueMatchType, FileKey, Deleted, SharedFileId, Files, Attributes)

        for k,v in kwargs.items():
            shared_file[k] = v

        return shared_file

    def to_notion(self):
        data = {'properties': {}}
        data['archived'] = False
        Property.set_property(data, self.Description, 'Description', property_type='title')
        Property.set_property(data, self.SharedFileId, 'SharedFileId', property_type='number')
        if self.FamilyObjectType:
            Property.set_property(data, self.FamilyObjectType, 'FamilyObjectType', property_type='select')
        Property.set_property(data, self.CategoryName, 'CategoryName')
        Property.set_property(data, self.ParameterName, 'ParameterName')
        Property.set_property(data, self.ParameterValue, 'ParameterValue')
        Property.set_property(data, self.Deleted, 'Deleted', 'checkbox')
        value = None
        if self.ParameterValueMatchType == 0:
            value = 'Equals'
        elif self.ParameterValueMatchType == 1:
            value = 'StartsWith'
        elif self.ParameterValueMatchType == 2:
            value = 'EndsWith'
        elif self.ParameterValueMatchType == 3:
            value = 'Contains'
        Property.set_property(data, value, 'ParameterValueMatchType', 'select')
        SharedAttributes = []
        if self.Attributes:
            for attribute in self.Attributes:
                # print(repr(attribute))
                attribute.to_notion()
                SharedAttributes.append(attribute.NotionPageId)

            Property.set_property(data, SharedAttributes, 'SharedAttributes', property_type='relation')
        # print(data)

        if self.NotionPageId:
            r = Page.update_page(self.NotionPageId, data)
        else:
            r = Page.create_page('Shared Rules', data)
        # print(r.json())


    @classmethod
    def from_notion(cls, json_dict, **kwargs):
        NotionPageId = json_dict['id']
        NotionParentId = json_dict['parent']['database_id']
        props = json_dict['properties']

        Description = Property.get_property(props, 'Description', "")
        FamilyObjectType = Property.get_property(props, 'FamilyObjectType', "")
        CategoryName = Property.get_property(props, 'CategoryName', "")
        ParameterName = Property.get_property(props, 'ParameterName', "")
        ParameterValue = Property.get_property(props, 'ParameterValue', "")
        ParameterValueMatchType = Property.get_property(props, 'ParameterValueMatchType', 0)
        Deleted = Property.get_property(props, 'Deleted', False)
        SharedFileId = Property.get_property(props, 'SharedFileId', 0)
        AttributesProp = Property.get_property(props, 'SharedAttributes')
        Attributes = []
        if AttributesProp:
            for _id in AttributesProp:
                url = settings.NOTION_PAGE+ _id
                response = requests.get(url, headers=settings.NOTION_HEADERS)
                if response.status_code in range(200, 299):
                    results = response.json()
                    shared_attribute = SharedAttribute.from_notion(results)
                    # print(shared_attribute)
                    Attributes.append(shared_attribute)
                else:
                    # print(Description)
                    print(response.text)

        shared_file = cls(Description=Description, FamilyObjectType=FamilyObjectType, CategoryName=CategoryName, ParameterName=ParameterName, ParameterValue=ParameterValue, ParameterValueMatchType=ParameterValueMatchType, PropertyName=None, PropertyValue=None, PropertyValueMatchType=None, FileKey=None, Deleted=Deleted, SharedFileId=SharedFileId, Files=None, Attributes=Attributes)
        shared_file.NotionPageId = NotionPageId
        shared_file.NotionParentId = NotionParentId

        for k,v in kwargs.items():
            shared_file[k] = v

        return shared_file

    @staticmethod
    def archive_notion(db_name):
        results = Page.query_database(db_name)
        for r in results:
            Page.archive_page(r['id'])

    @staticmethod
    def archive_db(id_list):
        pass

    def __repr__(self):
        return 'SharedFile(Description={}, FamilyObjectType={}, CategoryName={}, ParameterName={}, ParameterValue={}, ParameterValueMatchType={}, PropertyName={}, PropertyValue={}, PropertyValueMatchType={}, FileKey={self.FileKey}, Deleted={}, SharedFileId={}, Files={}, Attributes={})'.format(self.Description, self.FamilyObjectType, self.CategoryName, self.ParameterName, self.ParameterValue, self.ParmameterValueMatchType, self.PropertyName, self.PropertyValue, self.PropertyValueMatchType, self.FileKey, self.Deleted, self.SharedFileId, self.Files, self.Attributes)


class SharedAttribute(Parameter):
    def __init__(self, Name, Value, Deleted=False, DataType=None, ParameterType=None, Sort=0, Hidden=False, ParameterId=0, AttributeType=0, SharedAttributeId=0):
        super().__init__(Name, Value, Deleted, DataType, ParameterType, Sort, Hidden, ParameterId)
        self.AttributeType = AttributeType
        self.SharedAttributeId = SharedAttributeId
        self.NotionPageId = None
        self.NotionParentId = None
    
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
        AttributeType = json_dict.get('AttributeType')
        SharedAttributeId = json_dict.get('SharedAttributeId', 0)
        NotionPageId = json_dict.get('NotionPageId')
        NotionParentId = json_dict.get('NotionParentId')
        
        shared_attr = cls(Name, Value, Deleted, DataType, ParameterType, Sort, Hidden, ParameterId, AttributeType, SharedAttributeId)
        shared_attr.NotionPageId = NotionPageId
        shared_attr.NotionParentId = NotionParentId

        for k,v in kwargs.items():
            shared_attr[k] = v

        return shared_attr

    def to_notion(self):
        data = {'properties': {}}
        data['archived'] = False
        data['properties']['SharedAttributeId'] = {'number': self.SharedAttributeId}
        value = None
        if self.AttributeType == 0:
            value = 'Property'
        elif self.AttributeType == 1:
            value = 'Parameter'
        if value:
            Property.set_property(data, value, 'AttributeTypeDescription', 'select')
        Property.set_property(data, self.Name, 'Name', 'title')
        Property.set_property(data, self.Value, 'Value')
        Property.set_property(data, self.Deleted, 'Deleted', 'checkbox')
        if self.DataType:
            Property.set_property(data, self.DataType, 'DataType', 'select')
        if self.ParameterType:
            Property.set_property(data, self.ParameterType, 'ParameterType', 'select')
        Property.set_property(data, self.Sort, 'Sort', 'number')
        Property.set_property(data, self.Hidden, 'Hidden', 'checkbox')

        # print(data)
        # print(self.NotionPageId)

        if self.NotionPageId:
            r = Page.update_page(self.NotionPageId, data)
            
        else:
            r= Page.create_page('Shared Attributes', data)
        # print(r.json())


    @classmethod
    def from_notion(cls, json_dict, **kwargs):
        NotionPageId = json_dict['id']
        NotionParentId = json_dict['parent']['database_id']
        props = json_dict['properties']

        Name = Property.get_property(props, 'Name', "")
        Value = Property.get_property(props, 'Value', "")
        Deleted = Property.get_property(props, 'Deleted', False)
        DataType = Property.get_property(props, 'DataType')
        ParameterType = Property.get_property(props, 'ParameterType')
        Sort = Property.get_property(props, 'Sort')
        Hidden = Property.get_property(props, 'Hidden', False)
        ParameterId = 0
        AttributeType = Property.get_property(props, 'AttributeType', 0)
        SharedAttributeId = Property.get_property(props, 'SharedAttributeId', 0)

        shared_attr = cls(Name, Value, Deleted, DataType, ParameterType, Sort, Hidden, ParameterId, AttributeType, SharedAttributeId)
        shared_attr.NotionPageId = NotionPageId
        shared_attr.NotionParentId = NotionParentId
        for k,v in kwargs.items():
            shared_attr[k] = v

        return shared_attr


    def __repr__(self):
        return 'SharedAttribute(Name={}, Value={}, Deleted={}, DataType={}, ParameterType={}, Sort={}, Hidden={}, ParameterId={}, AttributeType={}, SharedAttributeId={})'.format(self.Name, self.Value, self.Deleted, self.DataType, self.ParameterType, self.Sort, self.Hidden, self.ParameterId, self.AttributeType, self.SharedAttributeId)

    def __str__(self):
        return '[{}] {}: {}'.format(self.SharedAttributeId, self.Name, self.Value)
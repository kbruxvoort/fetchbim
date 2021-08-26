import requests
import os
import settings
import html

from notion import Property
from dotenv import load_dotenv
load_dotenv()

BIMSERVICE_KEY=os.getenv('BIMSERVICE_KEY')
BOUNDING_BOX_ID = "8c7feebe-76c9-4374-a997-8c53bc1d13ef"

def get_ids(key='Public'):
    response = requests.get(settings.BIMSERVICE_ENDPOINTS[key])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print('ERROR!')
    except requests.exceptions.ConnectionError:
        print('CONNECTION ERROR!')

    return response.json()


def extract_fields_from_response(response_json):
    """Extract family data from bimservice"""
    data = {"properties": {}}

    ssgfid = response_json.get('familyId', '')
    Property.set_property(data, ssgfid, 'SSGFID')

    family_name = response_json.get('familyName', '')
    Property.set_property(data, family_name, 'Name', 'title')

    status_index = response_json.get('status', 2)
    if status_index == 0:
        status = 'Public'
    elif status_index == 1:
        status = 'Private'
    else:
        status = 'Work in Progress'
    Property.set_property(data, status, '_Status', 'select')

    props = response_json.get('properties')
    params = response_json.get('familyParameters')
    detail = [x['value'] for x in props if x['name'] == 'Detail']
    if detail:
        Property.set_property(data, Property.truncate(html.unescape(detail[0])), '_Detail')

    tech_data = [x['value'] for x in props if x['name'] == 'Technical Data']
    if tech_data:
        Property.set_property(data, Property.truncate(html.unescape(tech_data[0])), '_Technical Data')
    
    fam_design = [x['value'] for x in props if x['name'] == 'FamilyDesign']
    if fam_design:
        Property.set_property(data, Property.truncate(html.unescape(fam_design[0])), '_Family Design')

    tags = [x['value'] for x in props if x['name'] == 'Tags']
    if tags:
        Property.set_property(data, Property.truncate(tags[0].replace(',', '\n')), '_Tags')

    includes_pricing = [x['value'] for x in props if x['name'] == 'Includes Pricing']
    if includes_pricing:
        if includes_pricing[0] == 'Yes':
            includes_pricing = True
        else:
            includes_pricing = False
        Property.set_property(data, includes_pricing, '_Includes Pricing', 'checkbox')

    ada_compliant = [x['value'] for x in props if x['name'] == 'ADA Compliant']
    if ada_compliant:
        if ada_compliant[0] == 'Yes':
            ada_compliant = True
        else:
            ada_compliant = False
        Property.set_property(data, ada_compliant, '_ADA Compliant', 'checkbox')

    has_connectors = [x['value'] for x in props if x['name'] == 'Has MEP Connectors']
    if has_connectors:
        if has_connectors[0] == 'Yes':
            has_connectors = True
        else:
            has_connectors = False
    Property.set_property(data, has_connectors, '_Has MEP Connectors', 'checkbox')

    product_id = [x['value'] for x in props if x['name'] == 'product_id']
    if product_id:
        product_page = "https://fetchbim.com/catalog/product/view/id/" + product_id[0]
        Property.set_property(data, product_page, '_Product Page', 'url')

    revit_file_link = ''
    revit_file_size = 0
    revit_file_version = ''
    files = response_json.get('familyFiles')
    revit_files = [x for x in files if x['fileKey'] == 'FamilyRevitFile']
    if revit_files:
        revit_file_link = revit_files[0]['downloadLink']
        revit_file_size = int(revit_files[0]['fileLength']/1024)
        revit_file_version = revit_files[0]['version']
    Property.set_property(data, revit_file_link, '_Revit File Link', 'url')
    Property.set_property(data, revit_file_size, '_Revit File Size (kb)', 'number')
    Property.set_property(data, revit_file_version, '_Revit File Version')

    image_file_link = ''
    image_files = [x for x in files if x['fileKey'] == 'FamilyImageLarge']
    if image_files:
        image_file_link = image_files[0]['downloadLink']
    Property.set_property(data, image_file_link, '_Image URL', 'url')

    documents = ''
    all_files = ["[" + x["fileKey"] + "]" + " " + x["fileName"] + x["fileExtension"] for x in files]
    if all_files:
        documents = "\n".join(all_files)
    Property.set_property(data, Property.truncate(documents), "_Documents")

    long_descript = [x['parameterValue'] for x in params if x['parameterName'] == 'SSG_Long Description']
    if long_descript:
        Property.set_property(data, Property.truncate(long_descript[0]), '_Long Description')

    short_descript = [x['parameterValue'] for x in params if x['parameterName'] == 'SSG_Short Description']
    if short_descript:
        Property.set_property(data, Property.truncate(short_descript[0]), '_Short Description')

    zM = [x['parameterValue'] for x in params if x['parameterName'] == 'zM']
    if zM:
        Property.set_property(data, zM[0], '_zM')
    
    object_type = response_json.get('familyObjectType')
   
    




    # Query List
    # category_name = response_json.get('categoryName', '').split('/')[0]
    # omniclass = response_json.get('Omniclass')
    # bo_category = response_json.get('BIMobject Category')
    # bo_ifc = response_json.get('IFC')
    # keynote = response_json.get('Keynote')
    # assembly = response_json.get('Assembly Code')
    # if object_type == 'ModelGroup':
    #     notion_child_ids = []
    #     grouped_families = response_json.get('groupedFamilies')
    #     if grouped_families:
    #         for child in grouped_families:
    #             notion_child_ids.append(child.get('childFamilyId'))
    #         unique_list = set(notion_child_ids)
    #         if BOUNDING_BOX_ID in unique_list:
    #             unique_list.remove(BOUNDING_BOX_ID)

    return data
import requests
import settings

from json import dumps, loads

class Property:
    @staticmethod
    def get_property(dct, property_name, default=None):
        value = default
        prop = dct.get(property_name)
        # print(prop)
        if prop:
            property_type = prop.get('type')
            if prop[property_type]:
                # print(prop[property_type])
                if property_type == 'rich_text':
                    value = prop['rich_text'][0]['text']['content']
                elif property_type == 'number':
                    value =  prop['number']
                elif property_type == "select":
                    value = prop['select']['name']
                elif property_type == "multi-select":
                    value = [x['name'] for x in prop.get('multi_select', [])]
                elif property_type == "relation":
                    value = [x['id'] for x in prop.get('relation', [])]
                elif property_type == 'formula':
                    value = prop['formula']['string']
                elif property_type == 'title':
                    value = prop['title'][0]['text']['content']
                elif property_type == 'checkbox':
                    value = prop['checkbox']
                elif property_type == 'url':
                    value = prop['url']
                elif property_type == 'email':
                    value = prop['email']
                elif property_type == 'phone_number':
                    value = prop['phone_number']
                elif property_type == 'people':
                    value = prop['people']['object']
                elif property_type == 'date':
                    value = prop['date']['start']

        return value

    @staticmethod
    def set_property(dict, value, property_name, property_type='rich_text'):
        if property_type == 'rich_text':
            dict['properties'][property_name] = {property_type: [{"text": {"content": value}}]}
        elif property_type == 'title':
            dict['properties'][property_name] = {property_type: [{"text": {"content": value}}]}
        elif property_type == 'number':
            dict['properties'][property_name] = {property_type: value}
        elif property_type == 'url':
            dict['properties'][property_name] = {property_type: value}
        elif property_type == 'select':
            dict['properties'][property_name] = {property_type: {'name': value}}
        elif property_type == 'relation':
            if not isinstance(value, list):
                value = [value]
            value = [{"id": x} for x in value]
                # value = [{"id": value}]
            dict['properties'][property_name] = {property_type: value}
        # elif property_type == 'people':
        #     if isinstance(value, list):
        #         value = [{"object: user", "id": x} for x in value]
        #     else:
        #         value = [{"id": value}]
            # dict['properties'][property_name] = {property_type: []}
        # elif property_type == 'files':
        #     dict['properties'][property_name] = {property_type: value}
        elif property_type == 'checkbox':
            dict['properties'][property_name] = {property_type: value}

        return dict

    @staticmethod
    def truncate(value, limit=2000):
        if len(value) > limit:
            value = '{}...'.format(value[:limit-3])
        return value

class Page:
    # Create a page
    @staticmethod
    def create_page(parent_db_name, payload):
        parent_id = settings.NOTION_DATABASE_IDS[parent_db_name]
        payload['parent'] = {"database_id": parent_id}
        url = settings.NOTION_PAGE
        r = requests.post(url, data=dumps(payload), headers=settings.NOTION_HEADERS)
        return r

    # Update a page
    @staticmethod
    def update_page(page_id, payload):
        url = settings.NOTION_PAGE + page_id
        r = requests.patch(url, data=dumps(payload), headers=settings.NOTION_HEADERS)
        return r

    @staticmethod
    def archive_page(page_id):
        data = {'archived': True}
        return Page.update_page(page_id, data)

    @staticmethod
    def restore_page(page_id):
        data = {'archived': False}
        return Page.update_page(page_id, data)
        
    # Query database
    @staticmethod
    def query_database(db_name, filt=None):
        db_id = settings.NOTION_DATABASE_IDS[db_name]
        url = settings.NOTION_DATABASE + db_id + "/query"

        cursor = None
        results = []
        response = None
        # notion will only return 100 items at a time. this loops through until there are no more
        data = {}
        if filt:
            data['filter'] = filt
        while True:
            
            if cursor:
                data['start_cursor'] = cursor
            # print(data)

            response = requests.post(url, data=dumps(data), headers=settings.NOTION_HEADERS)
            if response.status_code in range(200, 299):
                response_json = response.json()
                results.extend(response_json["results"])
                more_pages = response["has_more"]
                if more_pages:
                    cursor = response["next_cursor"]
                else:
                    break
            else:
                print(response.text)
                break
        return results

class Filter:
    # Create filter
    @staticmethod
    def create_text_filter(value, condition='equals', database_property='title'):
        # {"filter": {"property": "code", "text": {"equals": omniclass}}}  
        return {"property": database_property, "text": {condition: value}}

    @staticmethod
    def create_number_filter(value, condition='equals', database_property='title'):
        # {"property": "Cost of next trip", "number": {"greater_than_or_equal_to": 2}
        return {"property": database_property, "number": {condition: float(value)}}




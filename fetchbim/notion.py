import requests
import json

from .utils import retry

from . import settings


def truncate(value, limit=2000):
    if len(value) > limit:
        value = "{}...".format(value[: limit - 3])
    return value


class PropertyType(object):
    TEXT = "rich_text"
    NUMBER = "number"
    BOOL = "checkbox"
    SELECT = "select"
    MULTISELECT = "multi_select"
    DATE = "date"
    PEOPLE = "people"
    FILES = "files"
    RELATION = "relation"
    FORMULA = "formula"
    TITLE = "title"


class Condition(object):
    EQUALS = "equals"
    NOT_EQUAL = "does_not_equal"
    CONTAINS = "contains"
    NOT_CONTAIN = "does_not_contain"
    STARTS = "starts_with"
    ENDS = "ends_with"
    EMPTY = "is_empty"
    NOT_EMPTY = "is_not_empty"


class NotionProperty:
    @staticmethod
    def get_property(dct, property_name, default=None):
        value = default
        prop = dct.get(property_name)
        # print(prop)
        if prop:
            property_type = prop.get("type")
            if prop[property_type]:
                # print(prop[property_type])
                if property_type == "rich_text":
                    value = prop["rich_text"][0]["text"]["content"]
                elif property_type == "number":
                    value = prop["number"]
                elif property_type == "select":
                    value = prop["select"]["name"]
                elif property_type == "multi-select":
                    value = [x["name"] for x in prop.get("multi_select", [])]
                elif property_type == "relation":
                    value = [x["id"] for x in prop.get("relation", [])]
                elif property_type == "formula":
                    value = prop["formula"]["string"]
                elif property_type == "title":
                    value = prop["title"][0]["text"]["content"]
                elif property_type == "checkbox":
                    value = prop["checkbox"]
                elif property_type == "url":
                    value = prop["url"]
                elif property_type == "email":
                    value = prop["email"]
                elif property_type == "phone_number":
                    value = prop["phone_number"]
                elif property_type == "people":
                    value = prop["people"]["object"]
                elif property_type == "date":
                    value = prop["date"]["start"]

        return value

    @staticmethod
    def set_property(dict, value, property_name, property_type="rich_text"):
        if value:
            prop_check = dict.get("properties")

            if not prop_check:
                dict["properties"] = {}
            if property_type == "rich_text":
                dict["properties"][property_name] = {property_type: [{"text": {"content": truncate(value)}}]}
            elif property_type == "title":
                dict["properties"][property_name] = {property_type: [{"text": {"content": value}}]}
            elif property_type == "number":
                dict["properties"][property_name] = {property_type: value}
            elif property_type == "url":
                dict["properties"][property_name] = {property_type: truncate(value, limit=1000)}
            elif property_type == "select":
                dict["properties"][property_name] = {property_type: {"name": value}}
            elif property_type == "relation":
                if not isinstance(value, list):
                    value = [value]
                value = [{"id": x.get("id")} for x in value]
                # value = [{"id": value}]
                dict["properties"][property_name] = {property_type: value}
            elif property_type == "files":
                if not isinstance(value, list):
                    value = [value]
                value = [{"type": "external", "name": x[0], "external": x[1]} for x in value]
                dict["properties"][property_name] = {property_type: value}
            # elif property_type == 'people':
            #     if isinstance(value, list):
            #         value = [{"object: user", "id": x} for x in value]
            #     else:
            #         value = [{"id": value}]
            # dict['properties'][property_name] = {property_type: []}
            # elif property_type == 'files':
            #     dict['properties'][property_name] = {property_type: value}
            elif property_type == "checkbox":
                dict["properties"][property_name] = {property_type: value}

        return dict


class NotionPage:
    # Create a page
    @staticmethod
    @retry
    def create(parent_db_name, payload):
        parent_id = settings.NOTION_DATABASE_IDS[parent_db_name]
        payload["parent"] = {"database_id": parent_id}
        url = settings.NOTION_PAGE
        r = requests.post(url, data=json.dumps(payload), headers=settings.NOTION_HEADERS)
        return r

    # Update a page
    @staticmethod
    @retry
    def update(page_id, payload):
        url = settings.NOTION_PAGE + page_id
        r = requests.patch(url, data=json.dumps(payload), headers=settings.NOTION_HEADERS)
        return r

    @staticmethod
    def archive(page_id):
        data = {"archived": True}
        return NotionPage.update(page_id, data)

    @staticmethod
    def restore(page_id):
        data = {"archived": False}
        return NotionPage.update(page_id, data)


class NotionFilter:
    def __init__(
        self,
        value,
        filter_type=PropertyType.TEXT,
        condition=Condition.EQUALS,
        property_name="title",
    ):
        self.value = value
        self.filter_type = filter_type
        self.condition = condition
        self.property_name = property_name

    def to_json(self):
        if isinstance(self.value, list):
            filter_list = []
            for v in self.value:
                filter_list.append(
                    {
                        "property": self.property_name,
                        self.filter_type: {self.condition: v},
                    }
                )
            return filter_list
        else:
            return {
                "property": self.property_name,
                self.filter_type: {self.condition: self.value},
            }

    def __repr__(self):
        return "NotionFilter(value={}, filter_type={}, condition={}, property_name={}".format(
            self.value, self.filter_type, self.condition, self.property_name
        )

    # Query database
    @retry
    def query(self, db_name):
        db_id = settings.NOTION_DATABASE_IDS[db_name]
        url = settings.NOTION_DATABASE + db_id + "/query"

        cursor = None
        results = []
        response = None
        # notion will only return 100 items at a time. this loops through until there are no more
        data = {}
        if self.value is not None:
            filt = self.to_json()
            if isinstance(filt, list):
                data["filter"] = {"or": filt}
            else:
                data["filter"] = filt
        while True:
            if cursor:
                data["start_cursor"] = cursor
            try:
                r = requests.post(url, data=json.dumps(data), headers=settings.NOTION_HEADERS)
                r.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                print("Http Error:", errh)
            except requests.exceptions.ConnectionError as errc:
                print("Error Connecting:", errc)
            except requests.exceptions.Timeout as errt:
                print("Timeout Error:", errt)
            except requests.exceptions.RequestException as err:
                print("OOps: Something Else", err)
            else:
                response_json = r.json()
                results.extend(response_json["results"])
                more_pages = response_json["has_more"]
                if more_pages:
                    cursor = response_json["next_cursor"]
                else:
                    break

        return results


class NotionDatabase:
    @staticmethod
    @retry
    def get_all(db_name):
        db_id = settings.NOTION_DATABASE_IDS[db_name]
        url = settings.NOTION_DATABASE + db_id + "/query"
        headers = settings.NOTION_HEADERS
        cursor = None
        results = []
        response = None
        data = {}

        while True:
            if cursor:
                data["start_cursor"] = cursor
            try:
                r = requests.post(url, data=json.dumps(data), headers=headers)
                r.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                print("Http Error:", errh)
            except requests.exceptions.ConnectionError as errc:
                print("Error Connecting:", errc)
            except requests.exceptions.Timeout as errt:
                print("Timeout Error:", errt)
            except requests.exceptions.RequestException as err:
                print("OOps: Something Else", err)
            else:
                response_json = r.json()
                results.extend(response_json["results"])
                more_pages = response_json["has_more"]
                if more_pages:
                    cursor = response_json["next_cursor"]
                else:
                    break

        return results

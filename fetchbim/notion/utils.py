from enum import Enum


class Condition(Enum):
    EQUALS = "equals"
    NOT_EQUAL = "does_not_equal"
    CONTAINS = "contains"
    NOT_CONTAIN = "does_not_contain"
    STARTS = "starts_with"
    ENDS = "ends_with"
    EMPTY = "is_empty"
    NOT_EMPTY = "is_not_empty"

    def __str__(self):
        return self.value


class PropertyType(Enum):
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

    def __str__(self):
        return self.value


def truncate(value: str, limit: int = 2000) -> str:
    if len(value) > limit:
        value = "{}...".format(value[: limit - 3])
    return value


# class Property(FetchModel):
#     pass


# class Page(FetchModel):
#     @staticmethod
#     def get_title(dct):
#         title = None
#         props = dct.get("properties")
#         if props:
#             for p in props:
#                 if props[p]["type"] == "title":
#                     title = props[p]["title"][0]["plain_text"]
#         return title

#     @staticmethod
#     def archive(page_id):
#         notion.pages.update(page_id=page_id, **{"archived": True})

#     @staticmethod
#     def restore(page_id):
#         notion.pages.update(page_id=page_id, **{"archived": False})

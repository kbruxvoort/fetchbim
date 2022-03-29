from fetchbim import n_client
from .page import Page


def truncate(value: str, limit: int = 2000) -> str:
    if len(value) > limit:
        value = "{}...".format(value[: limit - 3])
    return value


def get_all_pages(database_id: str, **kwargs) -> list[Page]:
    results = []
    cursor = None
    while True:
        response = n_client.databases.query(
            database_id=database_id, start_cursor=cursor
        )
        results.extend(response["results"])
        if response["has_more"] is False:
            break
        else:
            cursor = response["next_cursor"]

    return [Page(**result) for result in results]


def create_relation_dict(pages: list[Page], property_name="Name") -> dict:
    return {page.properties[property_name].get_value(): str(page.id) for page in pages}


def str2bool(string: str) -> bool:
    return string.lower() in ["yes", "true", "1"]

from . import client
from fetchbim.settings import BS_HEADERS


def get_ids(all_families=False):
    if all_families:
        path = "/Families/All"
    else:
        path = "/Families/All"
    client.headers = BS_HEADERS
    client.base_url = "https://bimservice.ssgbim.com/api/"
    response = client.get(path)
    return response.json()

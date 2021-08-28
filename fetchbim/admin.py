import requests
from . import settings


def get_family(guid: str):
    """Returns a python dictionary representing a family object from the admin database

    Args:
        guid (str): Unique Family Id
    """
    if settings.BIM_KEY:
        url = settings.GET_FAMILY.format(guid)
        headers = settings.BIM_HEADERS
        response = requests.get(url, headers=headers)
        if response.ok:
            response_json = response.json()
            if response_json:
                try: 
                    return response_json.get('BusinessFamilies', [])[0]
                except IndexError as e:
                    print('Family Is Deleted: {}'.format(e))


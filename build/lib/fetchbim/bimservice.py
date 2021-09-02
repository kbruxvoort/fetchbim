import requests

from fetchbim import settings


def get_ids(all_families=False):
    if all_families:
        url = settings.BS_GET_ALL_FAMILIES
    else:
        url = settings.BS_GET_PUBLIC_FAMILIES

    response = None
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print("HttpError: {}".format(http_err))
    except requests.exceptions.ConnectionError as err:
        print("Connection Error: {}".format(err))
    except Exception as e:
        print("Error: {}".format(e))

    return response.json()

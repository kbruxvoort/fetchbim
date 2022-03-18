from . import bs_client


def get_ids(all_families=False):
    if all_families:
        path = "/Families/All"
    else:
        path = "/Families/"
    response = bs_client.get(path)
    return response.json()

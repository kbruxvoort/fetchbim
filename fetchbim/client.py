import os
import requests

API_KEY = os.environ.get("BIM_KEY")


class FetchClient:
    """
    An easy-to-use Python wrapper for the FetchBIM API
    """

    def __init__(self, api_key="") -> None:
        if not api_key:
            self.api_key = API_KEY
        self.auth = {"Authorization": "Bearer {}".format(self.api_key), "Content-Type": "application/json"}
        BASE_URL = "https://www.ssgbim.com/api/"
        self.post_family_url = BASE_URL + "v2/Family/"
        self.get_family_url = BASE_URL + "v2/Home/Family/{}"
        self.delete_family_url = BASE_URL + "Family/{}"
        self.restore_family_url = BASE_URL + "/Family/{}/Restore"

    def _build_request(self, url, method="GET", data=None):
        """
        Wrapper around the api call.
        Args:
            url (str): API Endpoint URL
            method (str, optional): Request type. Defaults to 'GET'.
            data (dict, optional): JSON dictionary. Defaults to None.
        """
        response = requests.request(method, headers=self.auth, url=url, data=data)
        if response.ok:
            return response.json()

    def info(self, family_id):
        """
        Return info for a family given it's id
        Args:
            family_id (str): family SSGFID
        """
        if isinstance(family_id, int):
            family_id = str(family_id)
        family_url = self.get_family_url.format(family_id)
        data = self._build_request(family_url)
        return data

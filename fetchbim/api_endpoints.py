"""FetchBIM API Endpoints"""
import httpx

from lib2to3.pytree import Base
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, root_validator

from fetchbim.utils import to_camel
from .models import MatchType, ObjectType, SharedRule, Family, File


if TYPE_CHECKING:
    from fetchbim.client import BaseClient


class Endpoint:
    def __init__(self, parent: "BaseClient") -> None:
        self.parent = parent


class FilesEndpoint(Endpoint):
    def list(self, **kwargs: Any):
        response = self.parent.request(
            path="Files", method="GET", auth=kwargs.get("auth")
        )
        if response:
            return [File(**_file) for _file in response]

    def create(self, body: dict, **kwargs: Any):
        response = self.parent.request(
            path="Files", method="POST", body=body, auth=kwargs.get("auth")
        )
        if response:
            return File(**response)

    def update(self, body: dict, **kwargs: Any):
        response = self.parent.request(
            path=f"File", method="PATCH", body=body, auth=kwargs.get("auth")
        )

        if response:
            return File(**response)

    def replace(self, id: str, body: dict, **kwargs: Any):
        response = self.parent.request(
            path=f"File/{id}", method="PUT", body=body, auth=kwargs.get("auth")
        )

        if response:
            return File(**response)

    def search(
        self,
        name: Optional[str] = None,
        key: Optional[str] = None,
        extension: Optional[str] = None,
        id: Optional[int] = None,
        deleted: Optional[bool] = False,
        **kwargs: Any,
    ):
        params = {}
        if name:
            params["FileName"] = name
        if key:
            params["FileKey"] = key
        if extension:
            params["FileExtension"] = extension
        if id:
            params["fileId"] = id
        params["Deleted"] = deleted

        response = self.parent.request(
            path="/SharedFile/Families",
            method="POST",
            query=params,
            auth=kwargs.get("auth"),
        )

        if response:
            return [File(**_file) for _file in response]

    def retrieve(self, id: int):
        results = self.search(id=id)
        try:
            return results[0]
        except IndexError as e:
            print(f"No file found with id:", {id})

    def delete(self, id: int):
        return self.update(body={"FileId": id, "Deleted": True})

    def restore(self, id: int):
        return self.update(body={"FileId": id, "Deleted": False})

    def attach_to_family(self):
        pass

    def detach_from_family(self):
        pass

    def attach_to_rule(self):
        pass

    def detach_from_rule(self):
        pass


class FamiliesEndpoint(Endpoint):
    def list(self, public_only: bool = True, **kwargs: Any):
        base_url = "https://bimservice.ssgbim.com/api/"
        if public_only:
            url = base_url + "Families"
        else:
            url = base_url + "Families/All"
        try:
            response = httpx.get(url=url)
            return response.json()
        except httpx.HTTPError as e:
            print(e)

    def retrieve(self, id: str, **kwargs: Any):
        response = self.parent.request(
            path=f"v2/Home/Family/{id}", method="GET", auth=kwargs.get("auth")
        )
        try:
            return Family(**response["BusinessFamilies"][0])
        except IndexError as e:
            print(e)
        except KeyError as e:
            print(e)

    def create(self, body: dict, **kwargs: Any):
        return self.parent.request(
            path="v2/Family", method="POST", body=body, auth=kwargs.get("auth")
        )

    def update(self, body: dict, **kwargs: Any):
        return self.parent.request(
            path="/Family", method="PATCH", body=body, auth=kwargs.get("auth")
        )

    def delete(self, id: str, **kwargs: Any):
        return self.parent.request(
            path=f"family/{id}", method="DELETE", auth=kwargs.get("auth")
        )

    def restore(self, id: str, **kwargs: Any):
        return self.parent.request(
            path=f"Family/{id}/restore", method="POST", auth=kwargs.get("auth")
        )

    def search(
        self,
        family_object_type: Optional[ObjectType] = None,
        category_name: Optional[str] = None,
        parameter_name: Optional[str] = None,
        parameter_value: Optional[str] = None,
        parameter_match_type: Optional[MatchType] = None,
        property_name: Optional[str] = None,
        property_value: Optional[str] = None,
        property_match_type: Optional[MatchType] = None,
        file_key: Optional[str] = None,
        **kwargs: Any,
    ):
        data = {}
        data["FamilyObjectType"] = family_object_type
        data["CategoryName"] = category_name
        data["ParameterName"] = parameter_name
        data["ParameterValue"] = parameter_value
        data["ParameterValueMatchType"] = parameter_match_type
        data["PropertyName"] = property_name
        data["PropertyValue"] = property_value
        data["PropertyValueMatchType"] = property_match_type
        data["FileKey"] = file_key

        response = self.parent.request(
            path="/SharedFile/Families",
            method="POST",
            body=data,
            auth=kwargs.get("auth"),
        )

        if response:
            return [Family(**fam) for fam in response]


class SharedRulesEndpoint(Endpoint):
    def list(self, **kwargs: Any):
        response = self.parent.request(
            path="SharedFiles", method="GET", auth=kwargs.get("auth")
        )

        if response:
            return [SharedRule(**rule) for rule in response["SharedFiles"]]

    def retrieve(self, id: str, **kwargs: Any):
        response = self.parent.request(
            path=f"SharedFile/{id}", method="GET", auth=kwargs.get("auth")
        )
        if response:
            return SharedRule(**response)

    def create(self, body: dict, **kwargs: Any):
        return self.parent.request(
            path="SharedFile", method="POST", body=body, auth=kwargs.get("auth")
        )

    def retrieve_families(self, body: SharedRule | dict, **kwargs: Any):
        if isinstance(body, SharedRule):
            body = body.dict(
                by_alias=True,
                exclude={"name", "deleted", "files", "attributes", "families"},
            )

        response = self.parent.request(
            path=f"SharedFile/Families",
            method="POST",
            body=body,
            auth=kwargs.get("auth"),
        )

        if response:
            return [Family(**fam) for fam in response]

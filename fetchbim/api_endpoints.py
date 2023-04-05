"""FetchBIM API Endpoints"""
import httpx

# from lib2to3.pytree import Base
from typing import TYPE_CHECKING, Any, Optional

# from pydantic import BaseModel, root_validator

from fetchbim.utils import to_camel
from .models import MatchType, ObjectType, SharedRule, Family, File

from notion_client.typing import SyncAsync


if TYPE_CHECKING:
    from fetchbim.client import BaseClient


class Endpoint:
    def __init__(self, parent: "BaseClient") -> None:
        self.parent = parent


class FilesEndpoint(Endpoint):
    def list(self, **kwargs: Any) -> SyncAsync[Any]:
        return self.parent.request(path="Files", method="GET", auth=kwargs.get("auth"))

    def create(self, body: dict, **kwargs: Any) -> SyncAsync[Any]:
        return self.parent.request(
            path="Files", method="POST", body=body, auth=kwargs.get("auth")
        )

    def update(self, body: dict, **kwargs: Any) -> SyncAsync[Any]:
        return self.parent.request(
            path=f"File", method="PATCH", body=body, auth=kwargs.get("auth")
        )

    def replace(self, id: str, body: dict, **kwargs: Any) -> SyncAsync[Any]:
        return self.parent.request(
            path=f"File/{id}", method="PUT", body=body, auth=kwargs.get("auth")
        )

    def search(
        self,
        name: Optional[str] = None,
        key: Optional[str] = None,
        extension: Optional[str] = None,
        id: Optional[int] = None,
        deleted: Optional[bool] = False,
        **kwargs: Any,
    ) -> SyncAsync[Any]:
        params = {}
        if name:
            params["FileName"] = name
        if key:
            params["FileKey"] = key
        if extension:
            params["FileExtension"] = extension
        if id:
            params["FileId"] = id
        params["Deleted"] = deleted

        return self.parent.request(
            path="/SharedFile/Families",
            method="POST",
            query=params,
            auth=kwargs.get("auth"),
        )

    def retrieve(self, id: int) -> SyncAsync[Any]:
        return self.search(id=id)

    def delete(self, id: int) -> SyncAsync[Any]:
        return self.update(body={"FileId": id, "Deleted": True})

    def restore(self, id: int) -> SyncAsync[Any]:
        return self.update(body={"FileId": id, "Deleted": False})

    def attach_to_family(self) -> SyncAsync[Any]:
        pass

    def detach_from_family(self) -> SyncAsync[Any]:
        pass

    def attach_to_rule(self) -> SyncAsync[Any]:
        pass

    def detach_from_rule(self) -> SyncAsync[Any]:
        pass


class FamiliesEndpoint(Endpoint):
    def list(self, public_only: bool = True, **kwargs: Any) -> SyncAsync[Any]:
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

    def retrieve(self, id: str, **kwargs: Any) -> SyncAsync[Any]:
        return self.parent.request(
            path=f"v2/Home/Family/{id}", method="GET", auth=kwargs.get("auth")
        )
        # try:
        #     return Family(**response["BusinessFamilies"][0])
        # except IndexError as e:
        #     print(e)
        # except KeyError as e:
        #     print(e)

    def create(self, body: dict, **kwargs: Any) -> SyncAsync[Any]:
        return self.parent.request(
            path="v2/Family", method="POST", body=body, auth=kwargs.get("auth")
        )

    def update(self, body: dict, **kwargs: Any) -> SyncAsync[Any]:
        return self.parent.request(
            path="/Family", method="PATCH", body=body, auth=kwargs.get("auth")
        )

    def delete(self, id: str, **kwargs: Any) -> SyncAsync[Any]:
        return self.parent.request(
            path=f"family/{id}", method="DELETE", auth=kwargs.get("auth")
        )

    def restore(self, id: str, **kwargs: Any) -> SyncAsync[Any]:
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
    ) -> SyncAsync[Any]:
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

        return self.parent.request(
            path="/SharedFile/Families",
            method="POST",
            body=data,
            auth=kwargs.get("auth"),
        )


class SharedRulesEndpoint(Endpoint):
    def list(self, **kwargs: Any) -> SyncAsync[Any]:
        return self.parent.request(
            path="SharedFiles", method="GET", auth=kwargs.get("auth")
        )

    def retrieve(self, id: str, **kwargs: Any) -> SyncAsync[Any]:
        return self.parent.request(
            path=f"SharedFile/{id}", method="GET", auth=kwargs.get("auth")
        )

    def create(self, body: dict, **kwargs: Any) -> SyncAsync[Any]:
        return self.parent.request(
            path="SharedFile", method="POST", body=body, auth=kwargs.get("auth")
        )

    def retrieve_families(
        self, body: SharedRule | dict, **kwargs: Any
    ) -> SyncAsync[Any]:
        if isinstance(body, SharedRule):
            body = body.dict(
                by_alias=True,
                exclude={"name", "deleted", "files", "attributes", "families"},
            )

        return self.parent.request(
            path=f"SharedFile/Families",
            method="POST",
            body=body,
            auth=kwargs.get("auth"),
        )

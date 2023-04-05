import logging
import json
from abc import abstractclassmethod
from types import TracebackType
from typing import Any, Dict, List, Optional, Type, Union

import httpx
from pydantic import BaseModel
from httpx import Request, Response

from fetchbim.config import settings
from fetchbim.api_endpoints import FilesEndpoint, FamiliesEndpoint, SharedRulesEndpoint
from fetchbim.logging import make_console_logger


class ClientOptions(BaseModel):
    auth: Optional[str] = None
    timeout_ms: int = 60_000
    base_url: str = settings.prod_base_url
    log_level: int = logging.WARNING
    logger: Optional[logging.Logger] = None

    class Config:
        arbitrary_types_allowed = True


class BaseClient:
    def __init__(
        self,
        client: httpx.Client | httpx.AsyncClient,
        options: Optional[Dict[str, Any] | ClientOptions] = None,
        **kwargs: Any,
    ) -> None:

        if options is None:
            options = ClientOptions(**kwargs)
        elif isinstance(options, dict):
            options = ClientOptions(**options)

        self.logger = options.logger or make_console_logger()
        self.logger.setLevel(options.log_level)
        self.options = options

        self._clients: List[httpx.Client | httpx.AsyncClient] = []
        self.client = client

        self.families = FamiliesEndpoint(self)
        self.files = FilesEndpoint(self)
        self.shared_rules = SharedRulesEndpoint(self)

    @property
    def client(self) -> httpx.Client | httpx.AsyncClient:
        return self._clients[-1]

    @client.setter
    def client(self, client: httpx.Client | httpx.AsyncClient) -> None:
        # client.base_url = httpx.URL(self.options.base_url + "/v1/")
        client.base_url = httpx.URL(self.options.base_url)
        client.timeout = httpx.Timeout(timeout=self.options.timeout_ms / 1_000)
        client.headers = httpx.Headers(
            {
                "Content-Type": "application/json",
            }
        )
        if self.options.auth:
            client.headers["Authorization"] = f"Bearer {self.options.auth}"
        self._clients.append(client)

    def _build_request(
        self,
        method: str,
        path: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        auth: Optional[str] = None,
    ) -> Request:
        headers = httpx.Headers()
        if auth:
            headers["Authorization"] = f"Bearer {auth}"
        self.logger.info(f"{method} {self.client.base_url}{path}")
        self.logger.debug(f"=> {query} -- {body}")
        return self.client.build_request(
            method, path, params=query, json=body, headers=headers
        )

    def _parse_response(self, response: Response) -> Any:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            print(error)
            # try:
            #     body = error.response.json()
            #     code = body.get("code")
            # except json.JSONDecodeError:
            #     code = None
            # if code and is_api_error_code(code):
            #     raise APIResponseError(response, body["message"], code)
            # raise HTTPResponseError(error.response)
        else:
            body = response.json()
            self.logger.debug(f"=> {body}")

            return body

    @abstractclassmethod
    def request(
        self,
        path: str,
        method: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        auth: Optional[str] = None,
    ):
        # ) -> SyncAsync[Any]:
        # noqa
        pass


class Client(BaseClient):
    """Synchronous client for Fetch's API."""

    client: httpx.Client

    def __init__(
        self,
        options: Optional[Union[Dict[Any, Any], ClientOptions]] = None,
        client: Optional[httpx.Client] = None,
        **kwargs: Any,
    ) -> None:
        if client is None:
            client = httpx.Client()
        super().__init__(client, options, **kwargs)

    def __enter__(self) -> "Client":
        self.client = httpx.Client()
        self.client.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        self.client.__exit__(exc_type, exc_value, traceback)
        del self._clients[-1]

    def close(self) -> None:
        """Close the connection pool of the current inner client."""
        self.client.close()

    def request(
        self,
        path: str,
        method: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        auth: Optional[str] = None,
    ) -> Any:
        """Send an HTTP request."""
        request = self._build_request(method, path, query, body, auth)
        try:
            response = self.client.send(request)
        except httpx.TimeoutException as error:
            # raise RequestTimeoutError()
            print(error)
        else:
            return self._parse_response(response)


class AsyncClient(BaseClient):
    """Asynchronous client for Fetch's API."""

    client: httpx.AsyncClient

    def __init__(
        self,
        options: Optional[Union[Dict[str, Any], ClientOptions]] = None,
        client: Optional[httpx.AsyncClient] = None,
        **kwargs: Any,
    ) -> None:
        if client is None:
            client = httpx.AsyncClient()
        super().__init__(client, options, **kwargs)

    async def __aenter__(self) -> "AsyncClient":
        self.client = httpx.AsyncClient()
        await self.client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        await self.client.__aexit__(exc_type, exc_value, traceback)
        del self._clients[-1]

    async def aclose(self) -> None:
        """Close the connection pool of the current inner client."""
        await self.client.aclose()

    async def request(
        self,
        path: str,
        method: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        auth: Optional[str] = None,
    ) -> Any:
        """Send an HTTP request asynchronously."""
        request = self._build_request(method, path, query, body, auth)
        try:
            response = await self.client.send(request)
        except httpx.TimeoutException:
            raise RequestTimeoutError()
        return self._parse_response(response)

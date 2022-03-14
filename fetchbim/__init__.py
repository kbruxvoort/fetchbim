import httpx


from .config import settings
from notion_client import AsyncClient, Client


BIM_HEADERS = {
    "Authorization": "Bearer {}".format(settings.bim_auth_key),
    "Content-Type": "application/json",
}
DEV_HEADERS = {
    "Authorization": "Bearer {}".format(settings.dev_auth_key),
    "Content-Type": "application/json",
}


client = httpx.Client(base_url=settings.bim_base_url, headers=BIM_HEADERS)
dev_client = httpx.Client(base_url=settings.dev_base_url, headers=DEV_HEADERS)
async_notion = AsyncClient(auth=settings.notion_auth_key)
notion = Client(auth=settings.notion_auth_key)


from .fetch import (
    Status,
    LoadMethod,
    ObjectType,
    ParameterType,
    AttributeType,
    DataType,
    MatchType,
    Property,
    Parameter,
    File,
    FamilyType,
    GroupedFamily,
    Family,
    SharedAttribute,
    SharedRule,
)

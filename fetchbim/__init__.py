import os
import httpx

from pydantic import BaseSettings
from dotenv import load_dotenv

from notion_client import AsyncClient, Client

load_dotenv()

BIM_KEY = os.getenv("BIM_KEY")
DEV_KEY = os.getenv("DEV_KEY")
NOTION_KEY = os.getenv("NOTION_KEY")
TEAMS_WEBHOOK = os.getenv("TEAMS_WEBHOOK")


class APIKeyMissingError(Exception):
    pass


if BIM_KEY is None:
    raise APIKeyMissingError("All methods require an API key.")

BIM_HEADERS = {
    "Authorization": "Bearer {}".format(BIM_KEY),
    "Content-Type": "application/json",
}
DEV_HEADERS = {
    "Authorization": "Bearer {}".format(DEV_KEY),
    "Content-Type": "application/json",
}


client = httpx.Client(base_url="https://www.ssgbim.com/api/", headers=BIM_HEADERS)
dev_client = httpx.Client(base_url="https://fetch.devssg.com/api/", headers=DEV_HEADERS)
async_notion = AsyncClient(auth=NOTION_KEY)
notion = Client(auth=NOTION_KEY)


from .models.fetch import (
    Property,
    Parameter,
    File,
    FamilyType,
    GroupedFamily,
    Family,
    SharedAttribute,
    SharedRule,
)

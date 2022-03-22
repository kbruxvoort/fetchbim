import httpx
import notion_client


from fetchbim.config import settings

DEV = False

if DEV:
    base_url = settings.dev_base_url
    auth_key = settings.dev_auth_key
else:
    base_url = settings.prod_base_url
    auth_key = settings.prod_auth_key

HEADERS = {
    "Authorization": "Bearer {}".format(auth_key),
    "Content-Type": "application/json",
}

NOTION_HEADERS = {
    "Authorization": settings.notion_auth_key,
    "Content-Type": "application/json",
    "Notion-Version": settings.notion_version,
}
# client_options = notion_client.client.ClientOptions(
#     notion_version=settings.notion_version
# )

client = httpx.Client(base_url=base_url, headers=HEADERS)
bs_client = httpx.Client(base_url=settings.bs_base_url)
n2_client = httpx.Client(base_url=settings.notion_base_url, headers=NOTION_HEADERS)
n_client = notion_client.Client(auth=settings.notion_auth_key)
an_client = notion_client.AsyncClient(auth=settings.notion_auth_key)

from .bimservice import get_ids

import httpx
import notion_client


from fetchbim.config import settings


BIM_HEADERS = {
    "Authorization": "Bearer {}".format(settings.bim_auth_key),
    "Content-Type": "application/json",
}
BS_HEADERS = {
    "Authorization": "Bearer {}".format(settings.bs_auth_key),
    "Content-Type": "application/json",
}
DEV_HEADERS = {
    "Authorization": "Bearer {}".format(settings.dev_auth_key),
    "Content-Type": "application/json",
}

client_options = notion_client.client.ClientOptions(
    notion_version=settings.notion_version
)

client = httpx.Client(base_url=settings.bim_base_url, headers=BIM_HEADERS)
bs_client = httpx.Client(base_url=settings.bs_base_url, headers=BS_HEADERS)
dev_client = httpx.Client(base_url=settings.dev_base_url, headers=DEV_HEADERS)
n_client = notion_client.Client(auth=settings.notion_auth_key)
an_client = notion_client.AsyncClient(auth=settings.notion_auth_key)

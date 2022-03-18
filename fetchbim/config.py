from typing import Optional

from pydantic import BaseSettings, HttpUrl


class Settings(BaseSettings):
    bim_auth_key: Optional[str]
    bim_base_url: Optional[HttpUrl]
    bs_auth_key: Optional[str]
    bs_base_url: Optional[HttpUrl]
    dev_auth_key: Optional[str]
    dev_base_url: Optional[HttpUrl]
    notion_auth_key: Optional[str]
    notion_base_url: Optional[HttpUrl]
    notion_version: Optional[str]
    teams_webhook: Optional[HttpUrl]


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")

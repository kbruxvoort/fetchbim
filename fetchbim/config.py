from typing import Optional

from pydantic import BaseSettings, Field, HttpUrl


class Base(BaseSettings):
    prod_base_url: HttpUrl
    prod_auth_key: str
    dev_base_url: HttpUrl
    dev_auth_key: str
    bs_auth_key: str
    bs_base_url: HttpUrl
    notion_auth_key: str
    notion_base_url: HttpUrl
    notion_version: str
    teams_webhook: HttpUrl

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Base()
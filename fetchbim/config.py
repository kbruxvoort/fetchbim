from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    bim_auth_key: Optional[str]
    bim_base_url: Optional[str]
    dev_auth_key: Optional[str]
    dev_base_url: Optional[str]
    notion_auth_key: Optional[str]
    notion_base_url: Optional[str]
    notion_version: Optional[str]
    teams_webhook: Optional[str]

    # class Config:
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")

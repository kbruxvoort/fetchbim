from typing import Optional

from pydantic import BaseSettings


class FetchSettings(BaseSettings):
    auth_key: str
    base_url: str

    class Config:
        env_file = "fetch.env"
        env_file_encoding = "utf-8"


# class DevSettings(BaseSettings):
#     auth_key: str
#     base_url: str


# class NotionSettings(BaseSettings):
#     auth_key: str
#     base_url: str
#     version: str

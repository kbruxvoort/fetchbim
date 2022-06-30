import time
import requests


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


def truncate(value: str, limit: int = 2000) -> str:
    if len(value) > limit:
        value = "{}...".format(value[: limit - 3])
    return value


def retry(func, retries=3):
    def retry_wrapper(*args, **kwargs):
        attempts = 0
        while attempts < retries:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                print(e)
                time.sleep(2)
                attempts += 1

    return retry_wrapper

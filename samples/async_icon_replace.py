import os
import asyncio

from notion_client import AsyncClient


try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    print("Could not load .env because python-dotenv not found.")
else:
    load_dotenv()

NOTION_KEY = os.getenv("NOTION_KEY", "")

while NOTION_KEY == "":
    print("NOTION_KEY not found.")
    NOTION_KEY = input("Enter your integration token: ").strip()

notion = AsyncClient(auth=NOTION_KEY)
image_link = "https://img.icons8.com/stickers/344/expensive-2.png"


async def update_icons(page_ids, image_url):
    tasks = []
    for page_id in page_ids:
        data = {"page_id": page_id, "icon": {"type": "external", "external": {"url": image_url}}}
        tasks.append(notion.pages.update(**data))
    responses = await asyncio.gather(*tasks)
    return responses


async def main():
    full_results = []
    cursor = None
    while True:
        data = {
            "database_id": "f56ac916a3f049dda2df0f864ca63c62",
            "filter": {"property": "Content Type", "relation": {"contains": "1cdeeb4c75944df2abbe1f69f0100c97"}},
        }
        if cursor:
            data["start_cursor"] = cursor
        results = await notion.databases.query(**data)
        full_results.extend(results["results"])
        if results["has_more"]:
            cursor = results["next_cursor"]
        else:
            break
    # pages = results["results"]
    page_ids = [page["id"] for page in full_results]

    if page_ids:

        responses = await update_icons(page_ids, image_link)
        for res in responses:
            print(res["properties"]["Name"]["title"][0]["plain_text"])


if __name__ == "__main__":
    asyncio.run(main())

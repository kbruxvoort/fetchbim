import aiohttp
import asyncio
import settings
import time
import json
import notion

from requests.exceptions import HTTPError
from . import settings
from . import notion
from bimservice import get_ids, extract_fields_from_response
from family import Family
from aiohttp import ClientSession
from notion import Filter, Property

ssg_ids = get_ids("Public")

bim_url = "https://bimservice.ssgbim.com/api/Family/{}"
query_url = "https://api.notion.com/v1/databases/f56ac916a3f049dda2df0f864ca63c62/query"


start_time = time.time()


async def update_with_sem(session, data, notion_id, sem):
    url = f"https://api.notion.com/v1/pages/{notion_id}"
    async with sem:
        async with session.patch(url, data=json.dumps(data), headers=settings.NOTION_HEADERS) as response:
            response_json = await response.json()
            if response.status > 299:
                print(response_json)
            results = response_json.get("results")
            return results


async def fetch_with_sem(session, family_id, sem):
    filt = Filter.create_text_filter(family_id, database_property="SSGFID")
    data = {}
    data["filter"] = filt
    url = "https://api.notion.com/v1/databases/f56ac916a3f049dda2df0f864ca63c62/query"
    notion_id = ""
    async with sem:
        async with session.post(url, data=json.dumps(data), headers=settings.NOTION_HEADERS) as response:
            response_json = await response.json()
            results = response_json.get("results")
            if results:
                notion_id = results[0].get("id")
            return notion_id, family_id


async def fetch(session, family_id, notion_id):
    url = f"https://bimservice.ssgbim.com/api/Family/{family_id}"
    async with session.get(url) as response:
        response_json = await response.json()
        notion_json = extract_fields_from_response(response_json)
        return notion_json, notion_id


async def main(sem_count=10):
    tasks = []
    tasks2 = []
    tasks3 = []
    sem = asyncio.Semaphore(sem_count)
    async with ClientSession() as session:
        for family_id in ssg_ids:
            tasks2.append(asyncio.create_task(fetch_with_sem(session, family_id, sem)))
        notion_pages = await asyncio.gather(*tasks2)
        for notion_id, family_id in notion_pages:
            tasks.append(asyncio.create_task(fetch(session, family_id, notion_id)))

        pages_content = await asyncio.gather(*tasks)
        for data, _id in pages_content:
            tasks3.append(asyncio.create_task(update_with_sem(session, data, _id, sem)))
        responses = await asyncio.gather(*tasks3)

        # return pages_content
        return responses
        # return notion_pages


if __name__ == "__main__":
    # contents = asyncio.get_event_loop().run_until_complete(main())
    # pages = asyncio.get_event_loop().run_until_complete(main(25))
    responses = asyncio.get_event_loop().run_until_complete(main(25))
    # for res, notion_id in responses:
    # print(f'Family: {res.get("familyName")}, Notion Id: {notion_id}')
    # for page in pages:
    #     res = page.get('results')
    #     if res:
    #         print(res[0].get('id'))
    # print(len(contents))
    # print(len(pages))
print("--- %s seconds ---" % (time.time() - start_time))

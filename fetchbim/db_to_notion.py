import aiohttp
import asyncio
import settings
import time
import json

from requests.exceptions import HTTPError
from bimservice import get_ids
from family import Family
from aiohttp import ClientSession
from notion import Filter

ssg_ids = get_ids('All')
results = []



# def get_tasks(session):
#     tasks = []
#     for family_id in ssg_ids:
#         tasks.append(asyncio.create_task(session.get(settings.BIMSERVICE_BASE_URL + "Family/" + family_id)))
#     return tasks

# async def get_fam_data():
#     async with ClientSession() as session:
#         tasks = get_tasks(session)
#         responses = await asyncio.gather(*tasks)
start_time = time.time()

async def main():
    async with ClientSession() as session:
        tasks = []
        for family_id in ssg_ids:
            task = asyncio.create_task(run_program(family_id, session))
            tasks.append(task)
        await asyncio.gather(*tasks)

async def query_for_id(family_id, session):
    """Query for notion page id (asynchronously)"""
    db_id = settings.DATABASE_IDS['Content Calendar']
    url = settings.NOTION_DATABASE_ENDPOINT + db_id + "/query"
    response = None
    filt = Filter.create_text_filter(family_id, database_property='SSGFID')
    try:
        response = await session.request(method='POST', url=url, data=json.dumps(filt), headers=settings.NOTION_HEADERS)
        response.raise_for_status()
        print(f'Response status ({url}): {response.status}')
    except HTTPError as http_err:
        print(f'An HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'An error occurred: {err}')
    response_json = await response.json()
    return response_json.get('id')

async def post_family_data(page_id, session):
    """Post family data using bimservice (asynchronously)"""
    url = settings.NOTION_PAGE_ENDPOINT + page_id
    try:
        response = await session.request(method='POST', url=url, headers=settings.NOTION_HEADERS)
        response.raise_for_status()
        print(f'Response status ({url}): {response.status}')
    except HTTPError as http_err:
        print(f'An HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'An error occurred: {err}')
    response_json = await response.json()
    return (response_json, session)

async def run_program(family_id, session):
    """Wrapper for running program in an asynchronous manner"""
    try:
        response1 = await get_family_data(family_id, session)
        response2 = await query_for_id(family_id, session)
        # fam = Family.from_json(response)
        print(f"Response: {response1['familyName']}")
        # return response['familyName']
    except Exception as err:
        print(f"Exception occurred: {err}")
        pass


async def get_family_data(family_id, session):
    """Get family data using bimservice (asynchronously)"""
    url = settings.BIMSERVICE_BASE_URL + "Family/" + family_id
    try:
        response = await session.get(url)
        response.raise_for_status()
        print(f"Response status ({url}): {response.status}")
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error ocurred: {err}")
    response_json = await response.json()
    # print(response_json)
    return response_json

if __name__ == '__main__':
    fams = asyncio.get_event_loop().run_until_complete(main())
    # print(fams)
    # asyncio.run(main())



    # try:
    #     response = await session.request(method='GET', url=url, headers=settings.BIMSERVICE_HEADERS)
    #     response.raise_for_status()
    #     print(f'Response status ({url}): {response.status}')
    # except HTTPError as http_err:
    #     print(f'An HTTP error occurred: {http_err}')
    # except Exception as err:
    #     print(f'An error occurred: {err}')
    # response_json = await response.json()
    # return Family.from_json(response_json)

# families = asyncio.get_event_loop().run_until_complete(main())

print("--- %s seconds ---" % (time.time() - start_time))
import aiohttp
import asyncio
import json
import os

from requests.exceptions import HTTPError
from fetchbim import settings
from fetchbim.bimservice import get_ids
from aiohttp import ClientSession

ssgbim_ids = get_ids('All')

def extract_fields_from_response(response):
    """Extract family data from bimservice"""
    ssgfid = response.get('familyId', '')
    family_name = response.get('familyName', '')
    category_name = response.get('categoryName', '').split('/')[0]
    object_type = response.get('familyObjectType')
    status_index = response.get('status', 2)
    if status_index == 0:
        status = 'Public'
    elif status_index == 1:
        status = 'Private'
    else:
        status = 'Work in Progress'

    return (ssgfid, family_name, category_name, object_type, status)

async def get_family_data(family_id, session):
    """Get family data using bimservice (asynchronously"""
    url = settings.BIMSERVICE_BASE_URL + "Family/" + family_id
    try:
        response = await session.request(method='GET', url=url, headers=settings.BIMSERVICE_HEADERS)
        response.raise_for_status()
        print(f'Response status ({url}): {response.status}')
    except HTTPError as http_err:
        print(f'An HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'An error occurred: {err}')
    response_json = await response.json()
    return response_json

async def main(family_id, session):
    """Wrapper for running program in an asynchronous manner"""
    try:
        response = await get_family_data(family_id, session)
        parsed_response = extract_fields_from_response(response)
        print(f'Response: {json.dumps(parsed_response, indent=2)}')
    except Exception as err:
        print(f'Exception occurred: {err}')
        pass

async with ClientSession() as session:
    await asyncio.gather(*[main(family_id, session) for family_id in ssgbim_ids])

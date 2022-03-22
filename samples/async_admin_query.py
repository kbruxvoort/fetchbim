import asyncio

from fetchbim import get_ids, an_client, client
from fetchbim.fetch import Family


async def query_admin(fam_ids):
    tasks = []
    for fam_id in fam_ids:
        path = f"/Home/Family/{fam_id}"
        tasks.append(client.get(path))
    return await asyncio.gather(*tasks)


async def query_notion(fam_ids, database_id):
    tasks = []
    for fam_id in fam_ids:
        data = {
            "database_id": database_id,
            "filter": {
                "property": "SSGFID",
                "relation": {"equals": fam_id},
            },
        }
        tasks.append(an_client.databases.query(**data))
    responses = await asyncio.gather(*tasks)
    return responses


async def main():
    family_ids = get_ids()
    responses = await query_admin(family_ids)
    for response in responses:
        print(response.status_code)
        fam_dict = response.json()["BusinessFamilies"][0]
        fam = Family(**fam_dict)
        print(fam.name)


if __name__ == "__main__":
    asyncio.run(main())

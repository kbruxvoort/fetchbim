import asyncio
import time

from aiohttp import ClientSession
from fetchbim.admin import async_get_family
from fetchbim.bimservice import get_ids
from fetchbim.family import Family
from fetchbim.teams import sync_complete_msg


async def main(family_ids, sem_count=10):
    tasks = []
    async with ClientSession() as session:
        for family_id in family_ids:
            tasks.append(asyncio.create_task(async_get_family(family_id, session)))
        families = await asyncio.gather(*tasks)

        return families


start_time = time.time()

if __name__ == "__main__":
    family_ids = get_ids()
    families = asyncio.get_event_loop().run_until_complete(main(family_ids))

    print("--- %s seconds ---" % (time.time() - start_time))

    for fam in families:
        print(fam["Name"])

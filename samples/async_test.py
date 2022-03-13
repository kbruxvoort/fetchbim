import httpx
import asyncio

from fetchbim.settings import DEV_FAMILYFILES, DEV_GET_FAMILIYFILE, DEV_GET_FILE, DEV_HEADERS

base_url = "https://fetch.devssg.com/api/FamilyFiles?fileId="
file_ids = [str(i) for i in range(5000, 5050)]


async def log_request(request):
    print(f"Request: {request.method} {request.url}")


async def log_response(response):
    request = response.request
    print(f"Response: {request.method} {request.url} - Status {response.status_code}")


async def get_file_mappings(file_id):
    async with httpx.AsyncClient(event_hooks={"request": [log_request], "response": [log_response]}) as client:
        r = await client.get(f"{base_url}{file_id}", headers=DEV_HEADERS)
        results.append(r.json())
        return


async def main():
    tasks = []
    for i in range(5000, 5050):
        tasks.append(get_file_mappings(str(i)))
    await asyncio.gather(*tasks)


if __name__ == '__main__'
results = []
asyncio.run(main())

for res in results:
    for r in res:
        print(f"{r['FileId']}: {r['FamilyId']}")

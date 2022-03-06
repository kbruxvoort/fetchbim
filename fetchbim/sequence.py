import asyncio


async def run_sequence(*functions):
    for function in functions:
        await function


async def run_parallel(*functions):
    asyncio.gather(*functions)

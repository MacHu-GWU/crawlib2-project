# -*- coding: utf-8 -*-

from urls import url_list
import aiohttp
import asyncio
from sfm.timer import DateTimeTimer as Timer


async def fetch(url, session):
    async with session.get(url) as response:
        return await response.text(errors="ignore")


async def run():
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in url_list:
            task = asyncio.ensure_future(fetch(url, session))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        print([len(html) for html in responses])


with Timer("aiohttp"):
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run())
    loop.run_until_complete(future)

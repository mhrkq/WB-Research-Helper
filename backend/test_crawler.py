# NOT IN USE

import asyncio
from app.ingest.services.crawler import crawl_url

async def test_crawl():
    md, title = await crawl_url("https://warhammerfantasy.fandom.com/wiki/Skaven")
    print("Length of content:", len(md))
    print("Title:", title)

asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
asyncio.run(test_crawl())
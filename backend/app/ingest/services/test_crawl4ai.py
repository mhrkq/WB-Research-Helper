# NOT IN USE

import asyncio
from crawl4ai import *

# fit markdown crawling
# PruningContentFilter (also have BM25ContentFilter)
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def main():
    # Step 1: Create a pruning filter
    prune_filter = PruningContentFilter(
        # lower = more content retained, higher = more content pruned
        threshold=0.45,           
        # fixed/dynamic
        threshold_type="dynamic",  
        # ignore nodes with <5 words
        min_word_threshold=5      
    )

    md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)

    config = CrawlerRunConfig(
        markdown_generator=md_generator,
        # extract_head=True
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://warhammerfantasy.fandom.com/wiki/Skaven", 
            config=config
        )

        if result.success:
            # 'fit_markdown' is your pruned content, focusing on "denser" text
            if result.metadata:
                print("Page Title:", result.metadata.get("title"))
            print("Raw Markdown length:", len(result.markdown.raw_markdown))
            print("Fit Markdown length:", len(result.markdown.fit_markdown))
            # print(result.markdown)
        else:
            print("Error:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())

# crawler.py

# https://docs.crawl4ai.com/

import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

import logging

logger = logging.getLogger(__name__)

async def crawl_url(url: str) -> tuple[str, str]:
    """
    Crawl a URL asynchronously and return a tuple: (page_text, page_title).
    Uses crawl4ai.
    """
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
    
    logger.info(f"Crawling URL: {url}")

    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                # url="https://warhammerfantasy.fandom.com/wiki/Skaven", 
                url=url, 
                config=config
            )

            if result.success:
                # 'fit_markdown' is pruned content that focuses on "denser" text
                logger.info(f"Raw Markdown length: {len(result.markdown.raw_markdown)}")
                logger.info(f"Fit Markdown length: {len(result.markdown.fit_markdown)}")
                
                page_title = result.metadata.get("title") if result.metadata else None
                if result.metadata:
                    print("Page Title:", result.metadata.get("title"))
                md = result.markdown.fit_markdown
                return md, page_title
            else:
                print("Error:", result.error_message)
    
    except Exception as e:
        logger.error(f"Error crawling {url}: {e}")
        return "", None
import asyncio
import os
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.deep_crawling.filters import (
    FilterChain,
    URLPatternFilter,
    DomainFilter,
    ContentTypeFilter
)
from crawl4ai.async_configs import BrowserConfig
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai import RateLimiter
import argparse

async def main(url, depth, filter, output):
    # Create a chain of filters
    filter_chain = FilterChain([
        # Only follow URLs with specific patterns
        #URLPatternFilter(patterns=["*Online:*", "*Lore:*"]),
        URLPatternFilter(patterns=[filter]),
        # Only crawl specific domains
        #DomainFilter(
        #    allowed_domains=["docs.example.com"],
        #    blocked_domains=["old.docs.example.com"]
        #),

        # Only include specific content types
        ContentTypeFilter(allowed_types=["text/html"])
    ])
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=90.0,  # Pause if memory exceeds this
        check_interval=1.0,             # How often to check memory
        max_session_permit=10,          # Maximum concurrent tasks
        rate_limiter=RateLimiter(       # Optional rate limiting
            base_delay=(10.0, 20.0),
            max_delay=60.0,
            max_retries=2,
            rate_limit_codes=[429, 503]  # Handle these HTTP status codes
        )
    )
#    proxy_config = {
#        "server": "atlanta.us.socks.nordhold.net:1080",
#        "username": "",
#        "password": ""
#    }

    #browser_config = BrowserConfig(proxy_config=proxy_config)

    # Configure a 1-level deep crawl
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=depth, 
            include_external=False,
            filter_chain=filter_chain
        ),
        check_robots_txt=True,  # Will check and respect robots.txt rules
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
        stream=True,
        markdown_generator=DefaultMarkdownGenerator(
            options={"citations": True, "body_width": 80}  # e.g. pass html2text style options
        )
    )

    async with AsyncWebCrawler() as crawler:
        async for result in await crawler.arun(url, config=config, dispatcher=dispatcher):
            process_result(result, output)

        #print(f"Crawled {len(results)} pages in total")
    

def process_result(result, output):
        local_dir = output
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        # Access individual results
        #for result in results:
        url = result.url
        md_res = result.markdown
        if md_res != None:
            print(f"URL: {url}")
            print(f"Depth: {result.metadata.get('depth', 0)}")
            url_name = url.split("/")[-2] + '_' + url.split("/")[-1]
            if url_name != '':
                filename = os.path.join( local_dir, url_name + '.md')
            else:
                filename = os.path.join( local_dir, 'home' + '.md')
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    content = md_res.raw_markdown
                    if content != None:
                        f.write(content)
if __name__ == "__main__":
    parser = argparse.ArgumentParser("crawler")
    parser.add_argument("url", help="URL to crawl.", type=str)
    parser.add_argument("depth", help="depth to crawl", type=int)
    parser.add_argument("filter", help="list of string filters for saving pages", type=str)
    parser.add_argument("output", help="path of output directory", type=str)
    args = parser.parse_args()
    asyncio.run(main(args.url,args.depth,args.filter,args.output))

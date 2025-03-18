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

async def main():
    # Create a chain of filters
    filter_chain = FilterChain([
        # Only follow URLs with specific patterns
        #URLPatternFilter(patterns=["*Online:*", "*Lore:*"]),
        URLPatternFilter(patterns=["*Online:*"]),
        # Only crawl specific domains
        #DomainFilter(
        #    allowed_domains=["docs.example.com"],
        #    blocked_domains=["old.docs.example.com"]
        #),

        # Only include specific content types
        ContentTypeFilter(allowed_types=["text/html"])
    ])

    # Configure a 1-level deep crawl
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=3, 
            include_external=False,
            filter_chain=filter_chain
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
        stream=True,
        markdown_generator=DefaultMarkdownGenerator(
            options={"citations": True, "body_width": 80}  # e.g. pass html2text style options
        )
    )

    async with AsyncWebCrawler() as crawler:
        async for result in await crawler.arun("https://en.uesp.net/wiki/Online:Online", config=config):
            process_result(result)

        #print(f"Crawled {len(results)} pages in total")
    

def process_result(result):
        local_dir = "uesp_output2/"
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
            with open(filename, 'w') as f:
                content = md_res.raw_markdown
                if content != None:
                    f.write(content)
if __name__ == "__main__":
    asyncio.run(main())

from spider import Spider
import argparse
import os

def crawl(name, url):
    # Initialize the Spider with your API key
    app = Spider()

    # Crawl a website
    crawler_params = {
        'limit': 5000,
        'proxy_enabled': True,
        'store_data': True,
        'metadata': False,
        'request': 'smart_mode',
        'return_format': 'markdown'
    }
    crawl_result = app.crawl_url(url, params=crawler_params)
    print("crawl complete! Saving to files...")
    local_dir = os.path.join( 'context_files', 'md', name)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    for result in crawl_result:
        url_name = result['url'].split("/")[-1]
        if url_name != '':
            filename = os.path.join( local_dir, url_name + '.md')
        else:
            filename = os.path.join( local_dir, 'home' + '.md')
        print(filename)
        with open(filename, 'w') as f:
            content = result['content']
            if content != None:
                f.write(content)

def scrape(name, url):
    app = Spider()

    # scrape a single page
    scrape_params = {
        'proxy_enabled': True,
        'store_data': True,
        'metadata': False,
        'request': 'smart_mode',
        'return_format': 'markdown'
    }
    scraped_data = app.scrape_url(url, params=scrape_params)
    print("scrape complete! Saving to files...")
    local_dir = os.path.join( 'context_files', 'md', name)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    url_name = url.split("/")[-1]
    if url_name != '':
        filename = os.path.join( local_dir, url_name + '.md')
    else:
        filename = os.path.join( local_dir, 'home' + '.md')
    print(filename)
    with open(filename, 'w') as f:
        content = scraped_data[0]['content']
        if content != None:
            f.write(content)

parser = argparse.ArgumentParser("spider_crawl")
parser.add_argument("name", help="Short name of the website for identification.", type=str)
parser.add_argument("url", help="URL of the website to crawl.", type=str)
parser.add_argument("-mode", help="scrape | crawl to determine if a single page is scraped, or entire website is crawled.", type=str, choices=['scrape', 'crawl'], default='scrape', )
args = parser.parse_args()
if args.mode == 'crawl':
    crawl(name=args.name, url=args.url)
elif args.mode == 'scrape':
    scrape(name=args.name, url=args.url)
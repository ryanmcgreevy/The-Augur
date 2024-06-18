from spider import Spider
import argparse
import os
import json

def crawl(name, url):
    # Initialize the Spider with your API key
    app = Spider()

    # Crawl a website
    crawler_params = {
        'limit': 5000,
        'proxy_enabled': True,
        'store_data': False,
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
        url_name = result['url'].split("/")[-2] + '_' + result['url'].split("/")[-1]
        if url_name != '':
            filename = os.path.join( local_dir, url_name + '.md')
        else:
            filename = os.path.join( local_dir, 'home' + '.md')
        print(filename)
        with open(filename, 'w') as f:
            content = result['content']
            if content != None:
                f.write(content)

def crawl_stream(name, url):
    # Initialize the Spider with your API key
    app = Spider()

    # Crawl a website
    crawler_params = {
        'limit': 5000,
        'proxy_enabled': True,
        'store_data': False,
        'metadata': False,
        'request': 'smart_mode',
        'return_format': 'markdown'
    }
    crawl_result = app.crawl_url(url, params=crawler_params, stream=True, content_type="application/json")
    
    # local_dir = os.path.join( 'context_files_sub', 'md', name)
    # if not os.path.exists(local_dir):
    #     os.makedirs(local_dir)

    for result in crawl_result.iter_content():
        with open("stream_dump.json", 'ab') as f:
            f.write(result)
            
    json_data = []
    with open("stream_dump.json") as json_file: json_data = json.load(json_file)
    print("crawl complete! Saving to files...")
    local_dir = os.path.join( 'context_files_dump', 'md', name)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    for file in json_data:
        url_name = file['url'].split("/")[-2] + '_' + file['url'].split("/")[-1]
        if url_name != '':
            filename = os.path.join( local_dir, url_name + '.md')
        else:
            filename = os.path.join( local_dir, 'home' + '.md')
        with open(filename, 'w') as f:
            content = file['content']
            if content != None:
                f.write(content)


def scrape(name, url):
    app = Spider()

    # scrape a single page
    scrape_params = {
        'proxy_enabled': True,
        'store_data': False,
        'metadata': False,
        'request': 'smart_mode',
        'return_format': 'markdown'
    }
    scraped_data = app.scrape_url(url, params=scrape_params, stream=True, content_type="application/json")
    print("scrape complete! Saving to files...")
    local_dir = os.path.join( 'context_files_sub', 'md', name)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    url_name = url.split("/")[-2] + '_' + url.split("/")[-1]
    if url_name != '':
        filename = os.path.join( local_dir, url_name + '.md')
    else:
        filename = os.path.join( local_dir, 'home' + '.md')
    print(filename)
    with open(filename, 'w') as f:
        f.write(scraped_data.json()[0]['content'])
        # content = scraped_data[0]['content']
        # if content != None:
        #     f.write(content)
 

parser = argparse.ArgumentParser("spider_crawl")
parser.add_argument("name", help="Short name of the website for identification.", type=str)
parser.add_argument("url", help="URL of the website to crawl.", type=str)
parser.add_argument("-mode", help="scrape | crawl | stream to determine if a single page is scraped, or entire website is crawled in either default or streaming mode.", type=str, choices=['scrape', 'crawl', 'stream'], default='scrape', )
args = parser.parse_args()
if args.mode == 'crawl':
    crawl(name=args.name, url=args.url)
if args.mode == 'stream':
    crawl_stream(name=args.name, url=args.url)
elif args.mode == 'scrape':
    scrape(name=args.name, url=args.url)
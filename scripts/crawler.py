from typing import List
import requests
from xml.etree import ElementTree
import urllib3
import os
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from crawl4ai.async_configs import CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def crawl_parallel(urls: List[str], max_concurrent: int = 5, output_dir: str = "crawled_data"):
    """Crawl multiple URLs in parallel with a concurrency limit."""
    os.makedirs(output_dir, exist_ok=True)
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(),
        excluded_tags=['footer', 'nav', 'header'],
        css_selector='#kingster-page-wrapper',
        exclude_external_links=True,
        # Content processing
        process_iframes=True,
        remove_overlay_elements=True,

        # Cache control
        cache_mode=CacheMode.ENABLED  
    )

    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_url(url: str):
            async with semaphore:
                result = await crawler.arun(
                    url=url,
                    config=config,
                    session_id="session1"
                )
                if result.success:
                    print(f"Successfully crawled: {url}")
                    file_name = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_") + ".md"
                    file_path = os.path.join(output_dir, file_name)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result.markdown)
                else:
                    print(f"Failed: {url} - Error: {result.error_message}")
        
        # Process all URLs in parallel with limited concurrency
        await asyncio.gather(*[process_url(url) for url in urls])
    finally:
        await crawler.close()

def get_sitemap_urls_from_list(sitemap_urls: List[str]) -> List[str]:
    all_urls = []
    for sitemap_url in sitemap_urls:
        try:
            response = requests.get(sitemap_url.strip(), verify=False)
            response.raise_for_status()
            
            # Parse the XML
            root = ElementTree.fromstring(response.content)
            
            # Extract all URLs from the sitemap
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
            all_urls.extend(urls)
            
        except Exception as e:
            print(f"Error fetching sitemap {sitemap_url}: {e}")
    
    return all_urls

def get_all_sitemap_urls() -> List[str]:
    sitemap_urls = []
    
    # 1. All page sitemaps
    for i in range(1, 4):  # page-sitemap1.xml to page-sitemap3.xml
        sitemap_urls.append(f"https://giki.edu.pk/page-sitemap{i}.xml")
    
    # 2. All course sitemaps
    for i in range(1, 5):  # course-sitemap1.xml to course-sitemap4.xml
        sitemap_urls.append(f"https://giki.edu.pk/course-sitemap{i}.xml")
    
    # 3. All faculty sitemaps
    for i in range(1, 3):  # personnel-sitemap1.xml to personnel-sitemap2.xml
        sitemap_urls.append(f"https://giki.edu.pk/personnel-sitemap{i}.xml")
    
    # 4. All tribe events
    sitemap_urls.append("https://giki.edu.pk/tribe_events-sitemap.xml")
    
    # 5. All category different news
    sitemap_urls.append("https://giki.edu.pk/category-sitemap.xml")
    
    # 6. Admin stuff only few names (static URL)
    sitemap_urls.append("https://giki.edu.pk/portfolio_category/admin_staff/")
    
    return get_sitemap_urls_from_list(sitemap_urls)
    
async def main():
    urls = get_all_sitemap_urls()
    if not urls:
        print("No URLs found to crawl")
        return
    
    print(f"Found {len(urls)} URLs to crawl")
    await crawl_parallel(urls, output_dir="crawled_data")

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.async_configs import CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def main():
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

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://giki.edu.pk", config=config)

        if result.success:
            print("Raw Markdown Output:\n")
            print(result.markdown)  # The unfiltered markdown from the page
            
            file_name = "data/giki.md"
            with open(file_name, "w") as md_file:
                md_file.write(result.markdown)
            print(f"Results saved to : {file_name}")
        else:
            print("Crawl failed:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())

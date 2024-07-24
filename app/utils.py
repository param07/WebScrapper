from .scraper import Scraper
from config import PAGE_LIMIT, PROXY, SCRAPE_URL

def notifyScrapingResult(total):
    print(f"Scraping session has been completed. {total} products were scraped and updated in the database.")

async def scheduleScrape():
    scraper = Scraper(pageLimit = PAGE_LIMIT, proxy = PROXY, baseUrl = SCRAPE_URL)
    await scraper.scrape()
    notifyScrapingResult(scraper.getScrapedDataCount())
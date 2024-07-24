from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from .utils import scheduleScrape
import asyncio


def scheduleScrapeSync():
    asyncio.run(scheduleScrape())

def createScheduler():
    scheduler = BackgroundScheduler()

    # async def scrapeTask():
    #     scraper = Scraper(pageLimit=PAGE_LIMIT, proxy=PROXY, baseUrl=SCRAPE_URL)
    #     scraper.scrape()
    #     notifyScrapingResult(scraper.getScrapedDataCount())

    
    scheduler.add_job(func = scheduleScrapeSync, trigger='cron', hour = 3, minute = 45)
    return scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('app started...')
    scheduler = createScheduler()
    scheduler.start()
    yield
    print('app stopped')
    scheduler.shutdown(wait = False)
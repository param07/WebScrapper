from fastapi import FastAPI
from .scraper import Scraper
from config import PAGE_LIMIT, PROXY, SCRAPE_URL
from .utils import notifyScrapingResult
# from .scheduler import start_scheduler
import time

app = FastAPI()
# scheduler = start_scheduler(app)

@app.get('/')
async def root():
    return {"message": "Hello World"}

# access token pending

# two ways 
@app.post('/scrape')
async def scrape():
    scraper = Scraper(pageLimit = PAGE_LIMIT, proxy = PROXY, baseUrl = SCRAPE_URL)
    await scraper.scrape()
    notifyScrapingResult(scraper.getScrapedDataCount())
    # print(len(scraper.imageSet))
    return {"message": "Scraping of Data completed successfully"}


# def schedule_scraping():
#     scraper = Scraper(pageLimit=PAGE_LIMIT, proxy=PROXY, baseUrl=SCRAPE_URL)
#     scraper.scrape()
#     notifyScrapingResult(scraper.getScrapedDataCount())

# scheduler.add_job(schedule_scraping, 'cron', hour = 1, minute = 30)





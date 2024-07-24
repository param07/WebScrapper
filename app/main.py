from fastapi import FastAPI, Depends, HTTPException, status
from .scraper import Scraper
from config import PAGE_LIMIT, PROXY, SCRAPE_URL, ACCESS_TOKEN
from .utils import notifyScrapingResult
# from .scheduler import start_scheduler
from .scheduler import lifespan
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(lifespan=lifespan)
# scheduler = start_scheduler(app)

@app.get('/')
async def root():
    return {"message": "Hello World"}

security = HTTPBearer()

# access token verify
def verifyToken(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# two ways 
@app.post('/scrape')
async def scrape(token: HTTPAuthorizationCredentials = Depends(verifyToken)):
    scraper = Scraper(pageLimit = PAGE_LIMIT, proxy = PROXY, baseUrl = SCRAPE_URL)
    await scraper.scrape()
    notifyScrapingResult(scraper.getScrapedDataCount())
    # print(len(scraper.imageSet))
    return {"message": "Scraping of Data completed successfully"}

# scheduler.add_job(schedule_scraping, 'cron', hour = 1, minute = 30)





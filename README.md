# WebScrapper
A scraping tool using Python FastAPI framework to automate the information scraping process from the target SCRAPE_URL



## Setup and Run

For Windows, after checkout of the code

```bash
> python -m venv env            # To create virtual env
> .\env\Scripts\activate        # To activate virtual env
> pip install -r requirements.txt  # To install dependencies
> python main.py                # To run the application
```
## Environment Variables

To run this project, you will need to configure the following environment variables to your config.py file as per your requirements

`ACCESS_TOKEN`,
`SCRAPE_URL`,
`PAGE_LIMIT`,
`PROXY`,
`RETRY_COUNT`,
`RETRY_DELAY`,
`IMAGE_FOLDER`,
`JSON_FOLDER`,
`JSON_FILE_NAME`


## Features

- Get API : (/) : To check if application is up and running
- Post API : (/scrape) : To scrape data from SCRAPE_URL provided in config.py
- Scheduler : That will run and scrape data every day at default 3:45 am 
- Simple authentication added to the endpoint (/scrape) with ACCESS_TOKEN in config.py
- Retry mechanism for the scraping part. Number of retries : RETRY_COUNT after a delay of RETRY_DELAY configured in config.py
- Validation and data integrity of the product details using `pydantic`
- Scraping the product name, price, and image from each page
- Number of pages is determined based on PAGE_LIMIT and total available records
- Storing the scraped information in folder JSON_FOLDER and with filename JSON_FILE_NAME
- There is provision for providing proxy
- At the end of the scraping cycle, recipients are notified about the scraping status with message stating how many products were scraped.


## Design Choices

- Validation and data integrity of each of the product details is managed using `pydantic`
- Hit the base url to extract the total number of records and records on single page to determine the total available pages.
- Based on total available pages and PAGE_LIMIT the rest urls are hit asynchronously to fasten the process.
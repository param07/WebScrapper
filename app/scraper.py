from config import PAGE_LIMIT, PROXY, SCRAPE_URL, RETRY_COUNT, RETRY_DELAY, IMAGE_FOLDER
import requests
import time
from bs4 import BeautifulSoup
from math import ceil
import os
from .models import Product
import aiohttp
import asyncio
import json


class Scraper():
    def __init__(self, pageLimit = PAGE_LIMIT, proxy = PROXY, baseUrl = SCRAPE_URL):
        self.pageLimit = pageLimit
        self.proxy = proxy
        self.baseURL = baseUrl
        self.totalAvailPages = 0
        self.totalRecords = 0
        self.recordsPerPage = 0
        self.scrapedData = []
        # self.currRecordsCount = 0

    def hitURL(self, url):
        proxies = None
        if(self.proxy):
            proxies = {'http': self.proxy, 'https': self.proxy}

        return requests.get(url, proxies=proxies)
    
    def downloadImage(self, imageURL):
        imageRes = requests.get(imageURL)
        imageName = imageURL.split('/')[-1]
        imagePath = os.path.join(IMAGE_FOLDER, imageName)
        os.makedirs(os.path.dirname(imagePath), exist_ok=True)
        with open(imagePath, 'wb') as file:
            file.write(imageRes.content)
        return os.path.abspath(imagePath)
    
    def getPageDetails(self, cardsHTML):
        if(cardsHTML):
            for ind, card in enumerate(cardsHTML):
                product_title = ''
                product_price = 0.0
                path_to_image = ''
                # ele = {
                #     "product_title":"",
                #     "product_price":0,
                #     "path_to_image":"", # path to image at your PC
                # }
                heading = card.find('h2', {'class': 'woo-loop-product__title'})
                if(heading):
                    product_title = heading.text.strip()
                    print(product_title)

                price = card.find('span', {'class': 'price'})
                if(price and price.find('bdi')):
                    val = (price.find('bdi')).text.strip()
                    currency = ((price.find('bdi')).find('span', 'woocommerce-Price-currencySymbol')).text.strip()
                    product_price = float(val[1:])
                    print(product_price)

                image = card.find('div', {'class': 'mf-product-thumbnail'})
                if(image and image.find('img')):
                    imageTag = (image.find('img'))
                    imageURL = imageTag['src']
                    if('data-lazy-src' in imageTag.attrs):
                        # print('data-lazy-src')
                        imageURL = imageTag['data-lazy-src']
                    elif('data-lazy-srcset' in imageTag.attrs):
                        # print('data-lazy-srcset')
                        imageURL = imageTag['data-lazy-srcset'].split(',')[0].split()[0]
                    # print(imageURL)
                    path_to_image = self.downloadImage(imageURL)
                    # print(path_to_image)

                productData = Product(product_title=product_title, product_price=product_price, path_to_image=path_to_image)
                # print(productData)
                self.scrapedData.append(productData.model_dump())
                # self.currRecordsCount += 1

    async def getPage(self, session, url, proxies):
        for i in range(RETRY_COUNT):
            try:
                async with session.get(url, proxy=proxies) as res:
                    if(res.status == 200):
                        return await res.text()
                    else:
                        print(f"Retry {i+1}/{RETRY_COUNT} for URL: {url} due to status code {res.status}")
                        await asyncio.sleep(RETRY_DELAY)

            except Exception as e:
                print(f"Retry {i+1}/{RETRY_COUNT} for URL: {url} due to exception: {e}")
                await asyncio.sleep(RETRY_DELAY)

    async def getAllPages(self, session, urls, proxies):
        tasks = []
        for url in urls:
            task = asyncio.create_task(self.getPage(session, url, proxies))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return results
            
    async def startAsyncTasks(self, urls, proxies):
        async with aiohttp.ClientSession() as session:
            data = await self.getAllPages(session, urls, proxies)
            return data

    def parseResults(self, responses):
        for resp in responses:
            soup = BeautifulSoup(resp, 'html.parser')
            if(soup.find('div', {'class': 'product-inner'}) and soup.find_all('div', {'class': 'product-inner'})):
                allCards = soup.find_all('div', {'class': 'product-inner'})
                self.getPageDetails(allCards)

    def addDataToJson(self):
        with open('storage/scrapedData.json', 'w') as file:
            json.dump(self.scrapedData, file, indent=4)

    def scrape(self):
        # hit url first time to get total records and total pages
        isSuccess = False
        for i in range(RETRY_COUNT):
            try:
                res = self.hitURL(self.baseURL)
                if(res.status_code == 200):
                    html = BeautifulSoup(res.content, 'html.parser')
                    totalRecordsElem = html.find('div', {'class': 'products-found'})
                    cards = None
                    if(totalRecordsElem and totalRecordsElem.strong):
                        self.totalRecords = float(totalRecordsElem.strong.text.strip())
                        # print(self.totalRecords)
                    else:
                        return
                    # totalRecords = (html.find('div', {'class': 'products-found'}).strong.string)
                    if(html.find('div', {'class': 'product-inner'}) and html.find_all('div', {'class': 'product-inner'})):
                        self.recordsPerPage = float(len(html.find_all('div', {'class': 'product-inner'})))
                        cards = html.find_all('div', {'class': 'product-inner'})
                        # print(self.recordsPerPage)
                    else:
                        return
                    # recordsPerPage = (len(html.find_all('div', {'class': 'products'})))
                    if(self.totalRecords > 0):
                        self.totalAvailPages = ceil(self.totalRecords/self.recordsPerPage)
                        self.getPageDetails(cards)

                        # print(self.totalAvailPages)
                    else:
                        return
                    # print(self.totalAvailPages)
                    isSuccess = True
                    break
                else:
                    print(f"Retry {i+1}/{RETRY_COUNT} for URL: {self.baseURL} due to status code {res.status_code}")
                    time.sleep(RETRY_DELAY)
            except Exception as e:
                print(f"Retry {i+1}/{RETRY_COUNT} for URL: {self.baseURL} due to exception: {e}")
                time.sleep(RETRY_DELAY)

        if not isSuccess:
            print(f"Failed to fetch page {self.baseURL} after {RETRY_COUNT} retries.")
            return
        
        totalPages = min(self.totalAvailPages, self.pageLimit)
        if(totalPages > 1):                
            urls = []
            for page in range(2, totalPages + 1):
                pageUrl =  self.baseURL + f'page/{page}/'
                urls.append(pageUrl)

            proxies = None
            if(self.proxy):
                proxies = {'http': self.proxy, 'https': self.proxy}
            responses = asyncio.run(self.startAsyncTasks(urls, proxies))
            self.parseResults(responses)

        self.addDataToJson()


    def getScrapedDataCount(self):
        return len(self.scrapedData)


        




        

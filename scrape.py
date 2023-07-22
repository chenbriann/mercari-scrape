import asyncio
import ssl
import certifi
import aiohttp
import aiofiles
import utils
import os
from sqlite_database import SQLiteHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


async def download_image(session, url, item_id, semaphore, sslcontext) -> bool:
    try:
        async with semaphore:

            async with session.get(url, ssl=sslcontext, timeout=10) as response:
                if response.status == 200:
                    # Save image temporarily
                    print("dl")
                    filename = os.path.join(os.path.dirname(__file__), 'images', f'image_{item_id}.jpg')
                    async with aiofiles.open(filename, 'wb') as f:
                        await f.write(await response.read())
                        return True
    except Exception as e:
        print(f"Image Request Error: {e}")
        return False


async def process_item(session, item, db_handler, scrape_bot, semaphore, sslcontext):
    # Extract item details
    item_name = WebDriverWait(item, timeout=5).until(
        lambda i: (i.find_element(By.CSS_SELECTOR, '.itemName__a6f874a2')).text)
    item_price = WebDriverWait(item, timeout=5).until(
        lambda i: (
            int(i.find_element(By.CSS_SELECTOR, '.merPrice').text.replace('¥', '').replace(',', ''))))
    item_link = WebDriverWait(item, timeout=5).until(
        lambda i: (i.find_element(By.CSS_SELECTOR, 'div a')).get_attribute('href'))
    item_image_url = WebDriverWait(item, timeout=5).until(
        lambda i: (i.find_element(By.CSS_SELECTOR, 'picture img')).get_attribute('src')
    )

    print(item_name)
    # Search for keyword
    item_model = utils.match_keyword(item_name, db_handler)

    if (item_model != "No Match") and ("shops" not in item_link):
        item_id = utils.extract_id_from_link(item_link)

        # cache listing
        if db_handler.insert_listing(item_id, item_model, item_price):

            # Download image asynchronously
            image_found = await download_image(session, item_image_url, item_id, semaphore, sslcontext)

            # send new listing notification
            if image_found:
                filename = os.path.join(os.path.dirname(__file__), 'images', f'image_{item_id}.jpg')
                # await image_queue.join()
                async with aiofiles.open(filename, 'rb') as item_image:
                    await scrape_bot.send_listing_notification(item_model, item_price, item_link,
                                                               item_image)
                    os.remove(filename)
            else:
                await scrape_bot.send_listing_notification(item_model, item_price, item_link)
        # check watchlist for price drop
        elif db_handler.search_watchlist(item_id) is not None:
            utils.check_price_drop(item_id, item_price, db_handler)


async def scrape(link, scrape_bot):
    print("scrape started")
    await scrape_bot.send_message("scrape started")

    # Initialize WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)

    # Set concurrent limit for image requests
    semaphore = asyncio.Semaphore(utils.CONCURRENT_LIM)
    sslcontext = ssl.create_default_context(cafile=certifi.where())

    async with aiohttp.ClientSession() as session:
        # Initialize database handler
        db_handler = SQLiteHandler()
        db_handler.insert_model("oceanus")
        db_handler.insert_model("frogman")

        while utils.continue_scraping:
            # Get the filtered Mercari product page
            driver.get(link)

            # Explicitly wait for parent list of items
            item_list = WebDriverWait(driver, timeout=10).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, 'div#item-grid ul li'))

            # Process items asynchronously
            item_tasks = [
                process_item(session, item, db_handler, scrape_bot, semaphore, sslcontext)
                for item in item_list
            ]
            await asyncio.gather(*item_tasks)
            await asyncio.sleep(60)

    print("scrape stopped")
    await scrape_bot.send_message("scrape stopped")
    # Close WebDriver
    driver.quit()

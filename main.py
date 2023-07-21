import sys
from sqlite_database import SQLiteHandler
from database import DatabaseInterface
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class MatchingInterface(ABC):
    @abstractmethod
    def search(self, title: str) -> str:
        pass


def extract_id_from_link(link: str) -> int:
    """
    Get the item id integer from link
    :param link: item link
    :return: item id
    """
    return int((link.split('/')[-1])[1:])


def check_price_drop(id_num: int, new_price: int, db_handler: DatabaseInterface):
    """
    Check watched item for price change

    :param id_num: item id
    :param new_price: new item price
    :param db_handler: old item price
    :return: None
    """
    old_price = db_handler.search_watchlist(id_num)[2]
    if old_price != new_price:
        db_handler.update_watchlist_entry(id_num, new_price)
        # TODO notify price change


def main(link):
    # Initialize WebDriver
    driver = webdriver.Chrome()

    # # Initialize listing matcher
    # matcher = MatchingInterface()

    # Initialize database handler
    db_handler = SQLiteHandler()

    # Get the filtered Mercari product page
    driver.get(link)

    # Explicitly wait for parent list of items
    item_list = WebDriverWait(driver, timeout=10).until(
        lambda d: d.find_elements(By.CSS_SELECTOR, 'div#item-grid ul li'))

    for item in item_list:
        # Extract item details
        item_name = WebDriverWait(item, timeout=10).until(
            lambda i: (i.find_element(By.CSS_SELECTOR, '.itemName__a6f874a2')).text)
        item_price = WebDriverWait(item, timeout=10).until(
            lambda i: (int(i.find_element(By.CSS_SELECTOR, '.merPrice').text.replace('¥', '').replace(',', ''))))
        item_link = WebDriverWait(item, timeout=10).until(
            lambda i: (i.find_element(By.CSS_SELECTOR, 'div a')).get_attribute('href'))

        # # Search for keyword
        # item_model = matcher.search(item.text)

        # TODO get item model
        item_model = item_name
        if (item_model is not None) and ("shops" not in item_link):

            item_id = extract_id_from_link(item_link)

            # cache listing
            if db_handler.insert_listing(item_id, item_model, item_price):
                # TODO handle notification and user response from telegram
                print("new listing found")

            # check watchlist for price drop
            if db_handler.search_watchlist(item_id) is not None:
                check_price_drop(item_id, item_price, db_handler)
                # TODO send price drop notification

    # Close WebDriver
    driver.quit()


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python main.py <link>")
    else:
        arg1 = sys.argv[1]
        main(arg1)

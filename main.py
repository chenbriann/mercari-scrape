import sys
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class MatchingInterface(ABC):
    @abstractmethod
    def search(self, title: str) -> str:
        pass


class DatabaseInterface(ABC):
    @abstractmethod
    def create_database(self):
        pass

    @abstractmethod
    def get_all_listings(self) -> list[tuple[int, str, int]]:
        pass

    @abstractmethod
    def insert_listing(self, id_num: int, model: str, price: int):
        pass

    @abstractmethod
    def delete_listing(self, id_num: int):
        pass

    @abstractmethod
    def clear_all_listings(self):
        pass

    @abstractmethod
    def get_watchlist(self) -> list[tuple[int, str, int]]:
        pass

    @abstractmethod
    def add_to_watchlist(self, id_num: int, model: str, price: int):
        pass

    @abstractmethod
    def remove_from_watchlist(self, id_num: int):
        pass

    @abstractmethod
    def clear_watchlist(self):
        pass

    @abstractmethod
    def get_all_catalogued(self) -> list[tuple[int, str, int]]:
        pass

    @abstractmethod
    def insert_model(self, model: str, price: int):
        pass

    @abstractmethod
    def delete_model(self, model: str):
        pass

    @abstractmethod
    def clear_all_catalogued(self):
        pass


def extract_id_from_link(link: str) -> int:
    return int(link.split('/')[-1])


def main(link):
    # Initialize WebDriver
    driver = webdriver.Chrome()

    # Initialize listing matcher
    matcher = MatchingInterface()

    # Initialize database handler
    db_handler = DatabaseInterface()
    db_handler.create_database()

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

        # Search for keyword
        item_model = matcher.search(item.text)

        if item_model is not None:
            # cache listing
            db_handler.insert_listing(item, item_model, item_price)

        # TODO handle notification and user response from telegram

    # Close WebDriver
    driver.quit()


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python main.py <link>")
    else:
        arg1 = sys.argv[1]
        main(arg1)

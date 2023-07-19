from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

# Initialize WebDriver
driver = webdriver.Chrome()

# Get the filtered Mercari product page
driver.get(
    'Mercari link here')

# Explicitly wait for parent list of items
item_list = WebDriverWait(driver, timeout=10).until(lambda d: d.find_elements(By.CSS_SELECTOR, 'div#item-grid ul li'))

for item in item_list:
    # Extract item details
    item_name = WebDriverWait(item, timeout=10).until(lambda i: i.find_element(By.CSS_SELECTOR, '.itemName__a6f874a2'))
    item_price = WebDriverWait(item, timeout=10).until(lambda i: i.find_element(By.CSS_SELECTOR, '.merPrice'))
    item_link = WebDriverWait(item, timeout=10).until(
        lambda i: (i.find_element(By.CSS_SELECTOR, 'div a')).get_attribute('href'))

# Close WebDriver
driver.quit()

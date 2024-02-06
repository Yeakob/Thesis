import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import xlsxwriter
import os
import pygsheets

def get_total_pages(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    pagination_element = soup.find('ul', class_='pagination')
    if pagination_element:
        page_links = pagination_element.find_all('a', class_='page-link')
        if page_links:
            last_page_number = int(page_links[-2].text)
            return last_page_number
    return 1

def scrape_data(base_url):
    all_data = []

    total_pages = get_total_pages(base_url.format(1))
    print(f"Total Pages: {total_pages}")

    for page_number in range(1, 200):  # Iterate through all pages
        try:
            url = base_url.format(page_number)
            response = requests.get(url)

            driver.get(url)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Wait for the new results to load (adjust as needed)
            # Get the page source after scrolling
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            names = []
            prices = []

            product_elements = soup.select(".product .product-details .product-name")
            price_elements = soup.select(".product .product-details .product-pa-wrapper .product-price .new-price")
            if not product_elements:
                break

            for name_element, price_element in zip(product_elements, price_elements):
                names.append(name_element.get_text().strip())
                prices.append(price_element.get_text().strip().split('Tk ')[1])

            for i in range(len(names)):
                all_data.append({"Product_name": names[i], "Product_price": prices[i]})

            print(f"Data scraped from {url}")

        except Exception as e:
            print(f"Error scraping data from URL {url}: {e}")

    return all_data

def write_to_google_sheet(all_data):
    date = datetime.now().strftime("%Y-%m-%d").split('_')[0]
    date = str(date)
    creds_file = os.path.join('yeakub_credential.json')
    gc = pygsheets.authorize(service_file=creds_file)
    sh = gc.open("ThesisDataOthoba")
    worksheet_title = f"products-othoba-date:{date}"

    try:
        wks = sh.worksheet_by_title(worksheet_title)
    except pygsheets.exceptions.WorksheetNotFound:
        wks = sh.add_worksheet(worksheet_title)

    df = pd.DataFrame(all_data)
    wks.set_dataframe(df, start='A1')

# Set up Selenium webdriver with options
chrome_options = Options()
chrome_options.add_argument("--headless")  # To run Chrome in headless mode
chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.geolocation": 2})
service = Service('/usr/bin/chromedriver')  # Provide path to chromedriver executable
driver = webdriver.Chrome(service=service, options=chrome_options)

# Base URL to scrape with pagination
# base_url = 'https://www.othoba.com/furniture-big-saving-days-offers?pagenumber={}&orderby=0&pagesize=40'
base_url = 'https://www.othoba.com/food-grocery?pagenumber={}&orderby=0&pagesize=40'

all_data = scrape_data(base_url)

# Saving data to Google Sheet
write_to_google_sheet(all_data)

print("Data saved to Google Sheet successfully.")

# Close Selenium webdriver
driver.quit()

# get tenders id from page using bs

from bs4 import BeautifulSoup
import sqlite3
import time
''' since update of Firefox new conditions for webdriver'''
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service



""" If a site blocks bots, we need human being for selenium"""
# from fake_useragent import UserAgent
# useragent = UserAgent()
# profile = webdriver.FirefoxProfile()
# profile.set_preference("general.useragent.override", useragent.random)
# ua = UserAgent()
# user_agent = ua.random
# print(user_agent)
# options.add_argument(f'user-agent={user_agent}')
''' end of webdriver'''


def driver_get(link):
    print(f'Work with link... {link}')
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    service = Service(executable_path="/snap/bin/geckodriver")  # specify the path to your geckodriver
    driver = webdriver.Firefox(options=options, service=service)  # hide window of webdriver
    driver.implicitly_wait(10)
    driver.get(link)
    time.sleep(15)  # wait until page will be loaded
    html = driver.page_source
    driver.quit()
    bs = BeautifulSoup(html, 'html.parser')

    return bs


def find_links(bs):  # parsing links

    # Find all elements with the class 'search-result-card__description'
    id_values = []
    description_elements = bs.find_all(class_='search-result-card__description')

    # Extract and print the ID values
    for element in description_elements:
        id_text = element.find(string=lambda text: text and "ID:" in text)
        if id_text:
            id_values.append(id_text.replace("ID:", "").strip())
        else:
            print("N/A")

    # Print the list of ID values
    print(f'Get from page ids... {id_values}')
    return id_values


def paginator(soup):

    # Find all buttons with the class 'paginate__btn'
    page_buttons = soup.find_all(class_='paginate__btn')

    # Extract page numbers and filter out non-numeric values
    page_numbers = [int(button.text.strip()) for button in page_buttons if button.text.strip().isdigit()]

    # Find the maximum page number
    max_page_number = max(page_numbers) if page_numbers else 1

    print(f"Number of pages: {max_page_number}")
    return max_page_number


def get_id(ids):
    for i in ids:
        target_url = f"{url}{i}"
        print(f"Target url: {target_url}")
        bs_subpage = driver_get(target_url)

        # Find the div with class 'tender--head--inf'
        tender_info_div = bs_subpage.find('div', class_='tender--head--inf')

        # Extract the text content from the div
        div_content = tender_info_div.get_text(strip=True)

        # Split the content using '●' as a delimiter
        id_parts = div_content.split('●')

        # Extract the ID in hex from the second part
        id_in_hex = id_parts[1].strip()

        print(f"ID in hex: {id_in_hex}")
        id_url = [id_in_hex, target_url]
        insert_into_table(id_url)


def insert_into_table(data_variable):
    # Connect to the SQLite database (creates a new database if it doesn't exist)
    conn = sqlite3.connect('database.db')  # Replace 'your_database.db' with your desired database name

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    try:
        # Insert data into the table
        cursor.execute('''
            INSERT INTO tenders_2023 (prozorro_id, prozorro_url)
            VALUES (?, ?)
        ''', (data_variable[0], data_variable[1]))

        # Commit the changes to the database
        conn.commit()

        print("Data inserted successfully.")

    except sqlite3.Error as e:
        print(f"Error: {e}")

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()


if __name__ == "__main__":

    # відеоспостережен
    base_links = ['https://prozorro.gov.ua/search/tender?tender.start=2020-01-01&tender.end=2021-12-31&status=complete&text=%D0%B2%D1%96%D0%B4%D0%B5%D0%BE%D1%81%D0%BF%D0%BE%D1%81%D1%82%D0%B5%D1%80%D0%B5%D0%B6%D0%B5%D0%BD&sort=publication_date,desc',
                 'https://prozorro.gov.ua/search/tender?tender.start=2020-01-01&tender.end=2021-12-31&status=complete&text=%D0%B2%D1%96%D0%B4%D0%B5%D0%BE%D0%BD%D0%B0%D0%B3%D0%BB%D1%8F%D0%B4&sort=publication_date,desc',
                 'https://prozorro.gov.ua/search/tender?tender.start=2020-01-01&tender.end=2021-12-31&status=complete&text=%D0%B2%D1%96%D0%B4%D0%B5%D0%BE%D0%BA%D0%B0%D0%BC%D0%B5%D1%80&sort=publication_date,desc']

    for base_link in base_links:
        print(base_link)
        url = 'https://prozorro.gov.ua/tender/'
        bs = driver_get(base_link)
        number_pages = paginator(bs)
        for i in range(1, int(number_pages)):
            sub_link = f"{base_link}&page={i}"
            bs = driver_get(sub_link)
            id_values = find_links(bs)
            get_id(id_values)
        time.sleep(600)
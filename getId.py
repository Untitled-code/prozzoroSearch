# get tenders id from page using bs

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.error import URLError, HTTPError
import time
import shelve
import logging
from pathlib import Path
import csv
import smtplib
from email.mime.text import MIMEText # для работы с кириллицей
from email.header import Header
''' since update of Firefox new conditions for webdriver'''
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options

# from fake_useragent import UserAgent
# binary = FirefoxBinary(r'/usr/bin/firefox')
caps = DesiredCapabilities.FIREFOX.copy()
caps['marionette'] = True
# hide window of Webdriver
options = Options()
options.add_argument('--headless')
""" Site blocks botes, we need human being for selenium"""
#useragent = UserAgent()
# profile = webdriver.FirefoxProfile()
# profile.set_preference("general.useragent.override", useragent.random)
# ua = UserAgent()
# user_agent = ua.random
# print(user_agent)
# options.add_argument(f'user-agent={user_agent}')
''' end of webdriver'''

link = 'https://prozorro.gov.ua/search/tender?cpv=32230000-4&cpv=51310000-8&cpv=35120000-1&sort=publication_date,desc&status=complete&value.start=10000&value.end=&tender.start=2023-01-01&tender.end=2023-12-01'

def driverGet(link):
    driver = webdriver.Firefox(options=options)  # hide window of webdriver
    time.sleep(5)
    driver.get(link)
    time.sleep(5)
    html = driver.page_source
    # driver.close()
    bs = BeautifulSoup(html, 'html.parser')
    return bs


def findLinks(bs): #parsing links
    print(bs)
    divs = bs.find_all('div', {'class': 'search-result-card__title'})
    print(divs)

bs = driverGet(link)
findLinks(bs)
#import requests
#from bs4 import BeautifulSoup

#page = requests.get("https://www.redditmetis.com/user/iSquash")

#print(page.status_code)
#print(page)
#print(page.content)

#soup = BeautifulSoup(page.content, 'html.parser')

#print(soup.prettify())

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

def get_stats(driver):
    statname = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[1]/div/div[1]/div/div[2]/div/p').text
    stat = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[1]/div/div[1]/div/div[1]/div/p').text
    print(f"{statname.capitalize()}: {stat}")

    statname = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[1]/div/div[3]/div/div[2]/div/p').text
    stat = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[1]/div/div[3]/div/div[1]/div/p').text
    print(f"{statname.capitalize()}: {stat}")

    statname = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[1]/div/div[4]/div/div[2]/div/p').text
    stat = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[1]/div/div[4]/div/div[1]/div/p').text
    print(f"{statname.capitalize()}: {stat}")

driver = webdriver.Chrome("/home/kevin/Development/admissions-scripts/chromedriver")
WEBSITE = "https://redditmetis.com/user/"
USER = "dancingonfire"

SEARCH = f"{WEBSITE}{USER}"

driver.get(SEARCH)
import time
time.sleep(5)

try:
    get_stats(driver)
except NoSuchElementException:
    time.sleep(60)
    get_stats(driver)



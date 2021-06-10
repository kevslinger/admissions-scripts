from selenium import webdriver


driver = webdriver.Chrome("./chromedriver")
WEBSITE = "https://redditmetis.com/user/"
USER = "iSquash"

SEARCH = f"{WEBSITE}{USER}"

driver.get(SEARCH)

stat = driver.find_element_by_class_name("col-12 d-flex justify-content-center")
print(stat)



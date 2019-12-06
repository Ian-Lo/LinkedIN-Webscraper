#Adapted from https://github.com/lulu150003/Web-Scraping-Project
#sorry I don't know how to fork properly yet

# Load libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
from bs4 import BeautifulSoup
import pandas as pd

# Create values Selenium
USERNAME =  input("Enter username: ")
PASSWORD = input("Enter password: ")
SEARCH = input("Enter LI Search URL: ") #"https://www.linkedin.com/search/results/people/?facetGeoRegion=%5B%22my%3A0%22%5D&keywords=salesforce%20developer&origin=FACETED_SEARCH&page=51"
EMPLOYEE = 1000  # int(raw_input("Enter number of results: "))
linkedin = 'https://www.linkedin.com'

# Open Selenium
browser = webdriver.Chrome()
browser.get(linkedin)
time.sleep(3)

# Identify email and password inputs and enter in information
email = browser.find_element_by_name('session_key')
password = browser.find_element_by_name('session_password')
email.send_keys(USERNAME + Keys.RETURN)
password.send_keys(PASSWORD + Keys.RETURN)

# Go to URL search
time.sleep(1)
browser.get(SEARCH)
current_url = 'url_placeholder'  # this is a placeholder for the URL check

# Create empty dataframe
df = pd.DataFrame(columns=['name', 'title', 'location', 'profile'])

# Go through pages and download data
while True:

    # scroll around page to trigger lazy Loading
    time.sleep(1)
    browser.execute_script("window.scrollTo(0, 200);")
    time.sleep(1)
    browser.execute_script("window.scrollTo(0, 400);")
    time.sleep(1)
    browser.execute_script("window.scrollTo(0, 600);")
    time.sleep(1)
    browser.execute_script("window.scrollTo(0, 800);")
    time.sleep(1)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    # Check to see if url is the 100th page in search
    if current_url.find('page=100') != -1:
        break
    # Check to see if this url has been scraped before; break loop if it has
    previous_url = current_url
    current_url = browser.current_url
    if current_url == previous_url:
        break

    # Start scraping and filling in the dataframe
    page = BeautifulSoup(browser.page_source, 'lxml')
    page_names = page.find_all('span', class_='actor-name')
    page_titles = page.find_all('p', class_='subline-level-1')
    page_locations = page.find_all('p', class_='subline-level-2')
    page_profiles = page.find_all('a', class_='search-result__result-link')

    # Put scraped data into a dataframe
    names = list(map(lambda x: x.text, page_names))
    titles = list(map(lambda x: x.text.replace('\n', ''), page_titles))
    locations = list(map(lambda x: x.text.replace('\n', ''), page_locations))
    profiles = list(map(lambda x: linkedin + x['href'], page_profiles))[::2]
    temp = pd.DataFrame({'name': names, 'title': titles,
                         'location': locations, 'profile': profiles})

    # Filter out members who do not provide information
    temp = temp[temp['name'] != 'LinkedIn Member']

    # Append new data to df
    df = df.append(temp)
    df.to_csv("output_search.csv", index=False)

    # Stop appending if the number of retrieved records exceeds the limit
    if df.shape[0] >= EMPLOYEE:
        break

    # Find next button and hit next
    nextlabel = "//button[@aria-label='Next']"

    def check_exists_by_xpath(cname):
        try:
            browser.find_element_by_xpath(cname)
        except NoSuchElementException:
            return False
        return True

    if check_exists_by_xpath(nextlabel) == False:
        break
    nextt = browser.find_element_by_xpath(nextlabel)
    nextt.click()
    time.sleep(1)


# Reset dataframe index
df.reset_index()

# Export results
df.to_csv("output_search.csv", index=False)

# Close Selenium
browser.quit()

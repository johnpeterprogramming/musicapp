from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import time
import os
import requests

home_path = os.path.abspath(os.path.dirname("__file__"))

if not os.path.exists(os.path.join(home_path, 'Music')):
    os.mkdir('Music')

os.chdir(os.path.join(home_path, 'Music'))

options = Options()
options.headless = True

browser = webdriver.Firefox(options=options)

song_name = input("Song name: ")
# song_name = "eat that fetus"

browser.get('https://www.mp3juices.cc/')

search_bar = browser.find_element_by_name("query")
search_bar.send_keys(song_name)

search_button = browser.find_element_by_id("button")
search_button.click()
time.sleep(2)
search_button.click()
time.sleep(1)

first_result = browser.find_element_by_id("result_1")
download_button_of_result = first_result.find_element_by_link_text("Download")
download_button_of_result.click()

while True:
    try:
        download_button = browser.find_element_by_id("download_1")
        download_button_button = download_button.find_element_by_link_text("Download")
        download_link = download_button_button.get_attribute('href')
        browser.close()
        print("Found link, busying downloading")
        break
    except:
        pass

song_link = requests.get(download_link, allow_redirects=True)
open(song_name+".mp4", 'wb').write(song_link.content)

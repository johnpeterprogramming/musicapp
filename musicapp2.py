from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import time
import os
import requests

song_links = list()
song_names = ["meme machine", "enter sandman", "hjjhghfghyhjhj"]

home_path = os.path.abspath(os.path.dirname("__file__"))
os.chdir(home_path)
if not os.path.exists('Music'):
    os.mkdir('Music')

os.chdir('Music')


options = Options()
options.headless = True

browser = webdriver.Firefox(options=options)
from_start = time.time()

def get_song_link(song_name):
    browser.get('https://www.mp3juices.cc/')
    search_bar = browser.find_element_by_name("query")
    start = time.time()

    search_bar.send_keys(song_name)

    search_button = browser.find_element_by_id("button")
    search_button.click()
    time.sleep(2)
    search_button.click()
    start = time.time()
    while True:
        try:
            first_result = browser.find_element_by_id("result_1")
            download_button_of_result = first_result.find_element_by_link_text("Download")
            download_button_of_result.click()
            break
        except:
            if time.time() - start > 10:
                print("no search results for", song_name)
                break
    start = time.time()
    while True:
        try:
            download_button = browser.find_element_by_id("download_1")
            download_button_button = download_button.find_element_by_link_text("Download")
            download_link = download_button_button.get_attribute('href')
            print(f"Found link: {download_link}")
            song_links.append(download_link)
            break
        except:
            if time.time() - start > 10:
                print("Couldn't find link for", song_name)
                break
    

def download_song_link(song_link, song_name):
    song_link = requests.get(song_link, allow_redirects=True)
    open(song_name+".mp4", 'wb').write(song_link.content)


print("Enter song names. Type in 'q' to start downloading.")
while True:
    song_name = input("Song name: ")
    if song_name == "q":
        break
    song_names.append(song_name)

for song_name in song_names:
    get_song_link(song_name) 

print(f"takes {time.time()-from_start} to get all the links")

print("got all the links, downloading")
browser.close()

for song_link, song_name in zip(song_links, song_names):
    print("Downloading ", song_name)
    download_song_link(song_link, song_name)

print(time.time()-from_start)

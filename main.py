import spotipy
import spotipy.util as util

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# This opens a window in the background(headless) so it's faster and doesn't bother the user
options = Options()
options.headless = True

browser = webdriver.Firefox(options=options)

from pytube import YouTube

import os
os.chdir('Music')

# all current songs in Music folder so we don't download duplicates
songs = os.listdir()


default_client_id = 'e28b2678f2ce4edc9f3e1b2b52588c80'
default_client_secret = 'd787a0f00e6849a6845384e9a467119b'

scope = 'user-library-read'


# We have to turn this into two functions later
# get_video_link(name) returns the link of the youtube video with that search result
# download_video(link, location) downloads the youtube video link at a certain location
# the reason there should be two functions is because it takes the longest to actually get the link so we can use multiprocessing to improve efficiency
def download_video(name):
    if name+'.mp3' not in songs:
        link = 'https://www.youtube.com/results?search_query=' + name.replace(' ', '+')

        browser.get(link)

        soup = BeautifulSoup(browser.page_source, features="lxml")

        first_video_link = soup.find(id='video-title')
        if first_video_link:
            youtube_link = 'https://www.youtube.com'+first_video_link['href']
            print(youtube_link)
            yt = YouTube(youtube_link)
            filtered = yt.streams.filter(only_audio=True)

            stream = filtered[0]
            print('Starting Download')
            stream.download()
            os.rename(stream.default_filename, stream.default_filename.replace('.mp4', '.mp3'))
            print('Finished')


        else:
            print('not found')
    else:
        print(f'{name} already downloaded')



print('(1) Song')
print('(2) Album')
print('(3) Sync Spotify account')

options = int(input('> '))

if options == 1:
    name = input('Name of Song: ')
    download_video(name)

elif options == 2:
    print('Under contruction')

elif options == 3:
    print('Getting token for spotify api')
    token = util.prompt_for_user_token('Johna', scope, client_id=default_client_id, client_secret=default_client_secret, redirect_uri='http://localhost:8080')
    print('Gottem')

    sp = spotipy.Spotify(auth=token)
    print('Getting user saved tracks')
    results = sp.current_user_saved_tracks()

    for item in results['items']:
        name = item['track']['name']
        print('Finding ' + name)
        download_video(name)
        make_mp4()

    browser.close()

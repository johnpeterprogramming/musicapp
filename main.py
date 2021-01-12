import spotipy
import spotipy.util as util

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.options import Options




from pytube import YouTube


default_client_id = 'e28b2678f2ce4edc9f3e1b2b52588c80'
default_client_secret = 'd787a0f00e6849a6845384e9a467119b'

scope = 'user-library-read'

token = util.prompt_for_user_token('Johna', scope, client_id=default_client_id, client_secret=default_client_secret, redirect_uri='localhost:8080')

def download_video(name):
    link = 'https://www.youtube.com/results?search_query=' + name

    options = Options()
    options.headless = True

    browser = webdriver.Firefox(options=options)
    browser.get(link)

    soup = BeautifulSoup(browser.page_source, features="lxml")
    browser.close()


    first_video_link = soup.find(id='video-title')
    if first_video_link:
        youtube_link = 'https://www.youtube.com'+first_video_link['href']
        print('found')
    else:
        print('not found')


    print(youtube_link)


if token:
    print('token accepted')
    sp = spotipy.Spotify(auth=token)

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
        
        results = sp.current_user_saved_tracks()

        for item in results['items']:
            print(item['track']['name'])

else:
    print('No Token')









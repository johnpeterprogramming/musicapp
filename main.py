import spotipy
import spotipy.util as util

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True

browser = webdriver.Firefox(options=options)

from pytube import YouTube

import os
os.chdir('Music')


default_client_id = 'e28b2678f2ce4edc9f3e1b2b52588c80'
default_client_secret = 'd787a0f00e6849a6845384e9a467119b'

scope = 'user-library-read'



def download_video(name):
    link = 'https://www.youtube.com/results?search_query=' + name.replace(' ', '+')

    name = name.replace(' ', '_')

    
    browser.get(link)

    soup = BeautifulSoup(browser.page_source, features="lxml")
    


    first_video_link = soup.find(id='video-title')
    if first_video_link:
        youtube_link = 'https://www.youtube.com'+first_video_link['href']
        yt = YouTube(youtube_link)
        filtered = yt.streams.filter(only_audio=True)

        if filtered:
            print('Starting Download')
            filtered[0].download(filename=name)

            try:
                os.rename(name+'.mp4', name[:-4] + '.mp3')
                
            except:
                print("could't rename")
                print(f'file: ' + name + '.mp4')
                print('to: ' + name[:-4] + '.mp3')

            print('Finished')
            
        else:
            print('Nothing found')

    else:
        print('not found')
 


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
    token = util.prompt_for_user_token('Johna', scope, client_id=default_client_id, client_secret=default_client_secret, redirect_uri='http://localhost:8080')

    sp = spotipy.Spotify(auth=token)
    
    results = sp.current_user_saved_tracks()

    for item in results['items']:
        name = item['track']['name']
        print('Finding ' + name)
        download_video(name)
    browser.close()





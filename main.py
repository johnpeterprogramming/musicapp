#Spotify api
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#used to get the first youtube video link from search result
from bs4 import BeautifulSoup

#youtube's html is mostly rendered throught javascript so I cant use a simple get request i have to render it with selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# This opens a window in the background(headless) so it's faster and doesn't bother the user
options = Options()
options.headless = True

browser = webdriver.Firefox(options=options)

from pytube import YouTube

import os
import re # for punctuation filtering

import threading

client_id = 'e28b2678f2ce4edc9f3e1b2b52588c80'
client_secret = 'd787a0f00e6849a6845384e9a467119b'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp1 = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API

song_names = []
links = []

os.chdir('Music')
home_path = os.getcwd()

def get_song_info(name):
    result = sp1.search(name)
    track = result['tracks']['items'][0]

    #get artist data and display artist data
    artist = sp1.artist(track["artists"][0]["external_urls"]["spotify"])

    #get album data and display album data
    album = sp1.album(track["album"]["external_urls"]["spotify"])

    #assigning variables to replace special characters
    album_name = album["name"]
    artist_name = artist["name"]

    album_name = re.sub(r'[^\w\s]', '', album_name) #removes all punctuation
    artist_name = re.sub(r'[^\w\s]', '', artist_name)

    return artist_name, album_name

def append_video_link(name):

    link = 'https://www.youtube.com/results?search_query=' + name.replace(' ', '+')

    browser.get(link)

    soup = BeautifulSoup(browser.page_source, features="lxml")

    first_video_link = soup.find(id='video-title')

    links.append('https://www.youtube.com'+first_video_link['href'])


def download_video_link(link):
    yt = YouTube(link)
    filtered = yt.streams.filter(only_audio=True)

    stream = filtered[0]
    print('Starting Download')
    stream.download()
    os.rename(stream.default_filename, stream.default_filename.replace('.mp4', '.mp3'))
    print('Finished')



#Selection code. Will replace with GUI after main functionality completed
print('(1) Song Names')
print('(2) Album')

options = int(input('> '))

if options == 1:
    while 'q' not in song_names:
        song_names.append(input('q to finish> '))
    song_names.remove('q')

elif options == 2:
    # find album by name
    album = input("Name of album: ")
    results = sp1.search(q="album:" + album, type="album")

    # get the first album uri
    album_id = results['albums']['items'][0]['uri']

    # get album tracks
    tracks = sp1.album_tracks(album_id)
    for track in tracks['items']:
        name = track['name']
        song_names.append(name)

else:
    print('We didn\t understand, try again')

threads = []

#os.path.normpath()
#os.path.join()

for name in song_names:
    thread = threading.Thread(target=append_video_link, args=(name,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

for link in links:
    download_video_link(link)

#Spotify api
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#used to get the first youtube video link from search result
from bs4 import BeautifulSoup, element

import time

from pytube import YouTube

import os
import re # for punctuation filtering

from pydub import AudioSegment

#youtube's html is mostly rendered throught javascript so I cant use a simple get request i have to render it with selenium
from selenium import webdriver

#so i can enable headless
from selenium.webdriver.firefox.options import Options

import tkinter

window = tkinter.Tk()
window.geometry("400x180")
window.title("Music Downloader")

lbl = tkinter.Label(window, text="Enter name of songs(listable) or album", font=("Arial Bold", 16))
lbl.grid(column=0, row=0)

lbl1 = tkinter.Label(window, font=("Arial", 10))
lbl1.grid(column=0, row=5)

txt = tkinter.Entry(window,width=30)
txt.grid(column=0, row=1)

options = Options()
options.headless = True

browser = webdriver.Firefox(options=options)

client_id = 'e28b2678f2ce4edc9f3e1b2b52588c80'
client_secret = 'd787a0f00e6849a6845384e9a467119b'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp1 = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API

song_names = []
links = []

os.chdir('Music')
home_path = os.getcwd()

def append_video_link(name):
    lbl1.config(text=f'Getting link for {name}')

    link = 'https://www.youtube.com/results?search_query=' + name.replace(' ', '+')

    browser.get(link)

    soup = BeautifulSoup(browser.page_source, features="lxml")

    first_video_link = soup.find(id='video-title')

    links.append('https://www.youtube.com' + first_video_link['href'])

def get_song_info(name):
    result = sp1.search(name)
    track = result['tracks']['items'][0]

    #assigning variables to replace special characters
    album_name = track['album']["name"]

    artist_name = track['album']['artists'][0]['name']
    song_name = track['name']
    release_date = track['album']['release_date']
    release_date = release_date[:4] # only year


    album_name = re.sub(r'[^\w\s]', '', album_name) #removes all punctuation
    artist_name = re.sub(r'[^\w\s]', '', artist_name)
    
    file_path = os.path.join(artist_name, album_name)

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    return file_path, artist_name, album_name, song_name, release_date


def download_video_link(link, location, artist_name, album_name, song_name, release_date):
    yt = YouTube(link)

    filtered = yt.streams.filter(only_audio=True)

    stream = filtered[0]
    lbl1.config(text='Starting Download')
    stream.download(location)
#    os.rename(os.path.join(location, song_name+'.mp4'), os.path.join(location, song_name+'.mp3'))
    lbl1.config(text='Finished Download, adding metadata')

    audio = AudioSegment.from_file(os.path.join(location, stream.default_filename))

    os.remove(os.path.join(location, stream.default_filename))

    audio.export(os.path.join(location, song_name.replace(' ', '_'))+'.mp3', format='mp3', tags={'album':album_name, 'artist':artist_name, 'title':song_name, 'year':release_date})

    lbl1.config(text=f'Metadata for {song_name} added')

def download_song():
    song_name_name = txt.get()
    song_names.append(song_name_name)
    lbl1.config(text=str(song_names))

btn_song = tkinter.Button(window, text="Download Song", command=download_song)
btn_song.grid(column=0, row=2)

def download_album():
    # find album by name
    try:
        album = txt.get()
        results = sp1.search(q="album:" + album, type="album")

        # get the first album uri
        album_id = results['albums']['items'][0]['uri']

        # get album tracks
        tracks = sp1.album_tracks(album_id)
        for track in tracks['items']:
            name = track['name']
            song_names.append(name)
    except:
        lbl1.config(text="We did not understand, Please try again")

btn_album = tkinter.Button(window, text="Download Album", command=download_album)
btn_album.grid(column=0, row=3)

threads = []

#os.path.normpath()
#os.path.join()
def done():
    lbl1.config(text="Downloading")
    if __name__ == '__main__':

        start = time.perf_counter()

        for song_name in song_names:
            append_video_link(song_name)

        browser.close()

        for link, song_name in zip(links, song_names):
            file_path, artist_name, album, song, year = get_song_info(song_name)
            download_video_link(link, file_path, artist_name, album, song, year)

        end = time.perf_counter()

        lbl1.config(text=f'Done, this took {end-start} seconds')

btn_done = tkinter.Button(window, text="Start downloads", command=done)
btn_done.grid(column=0, row=4)
window.mainloop()


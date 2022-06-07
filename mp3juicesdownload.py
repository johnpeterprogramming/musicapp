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

#youtube's html is mostly rendered through javascript so I cant use a simple get request i have to render it with selenium
from selenium import webdriver

#so i can enable headless
from selenium.webdriver.firefox.options import Options

import pygame

import ntpath

from mutagen.mp3 import MP3

import tkinter


#Define starting setting for window

window = tkinter.Tk()
window.geometry("600x600")
window.title("Music Downloader")

#Create frame for downloader portion
frame = tkinter.Frame(window, bg='#4C4C4C')
frame.place(relwidth=1, relheight=0.6)


#Create Label, Entry and text box
caption = tkinter.Label(frame, text="Add songs or album to be downloaded", font=("Arial Bold", 16), bg='#4C4C4C', fg='white')
caption.place(relx=0.1, relwidth=0.8, relheight=0.05)

status_text = tkinter.Text(frame, font=("Arial", 10), bg='#999191')
status_text.place(relx=0.1, rely=0.4, relwidth=0.8, relheight=0.5)

inpBox = tkinter.Entry(frame,width=30, bg='#999191')
inpBox.place(relx=0.3, rely=0.1, relwidth=0.4, relheight=0.05)


#Define the menu bar
menump = tkinter.Menu(window)
window.config(menu=menump)

#Save the current working directory to variable
home_path = os.path.abspath(os.path.dirname("__file__"))
os.chdir(home_path)

if not os.path.exists('Music'):
    os.makedir('Music')

#Selenium browser

options = Options()
options.headless = True

browser = webdriver.Firefox(options=options)

#Initialise spotipy variables
client_id = 'e28b2678f2ce4edc9f3e1b2b52588c80'
client_secret = 'd787a0f00e6849a6845384e9a467119b'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp1 = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API

#Initialise downloader variables
song_names = []
links = []


os.chdir('Music')

def append_video_link(name):
    # status_text.insert('1.0', f'Getting link for {name}\n')

    link = 'https://www.youtube.com/results?search_query=' + name + '+' + get_song_info(name)[1]#artist name

    browser.get(link)

    soup = BeautifulSoup(browser.page_source, features="lxml")

    first_video_link = soup.find(id='video-title')
    if first_video_link:
        links.append('https://www.youtube.com' + first_video_link['href'])
        print('link: https://www.youtube.com' + first_video_link['href'] + ' successfully added.')
    else:
        print('coulndt find link')


def get_song_info(name):
    result = sp1.search(name)
    if result['tracks']['items'][0]:
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
    else:
        print(f'couldnt get song info of {name} from spotify api')


def download_video_link(link, location, artist_name, album_name, song_name, release_date):
    yt = YouTube(link)

    filtered = yt.streams.filter(only_audio=True)

    stream = filtered[0]

    print('Starting Download')
    print(location)
    stream.download(location)
    print(os.path.join(location, stream.default_filename))

    print('Finished Download, adding metadata')

    audio = AudioSegment.from_file(os.path.join(location, stream.default_filename))

    audio.export(os.path.join(location, song_name.replace(' ', '_'))+'.mp3', format='mp3', tags={'albumartist':artist_name,'album':album_name, 'artist':artist_name, 'title':song_name, 'year':release_date})

    os.remove(os.path.join(location, stream.default_filename))

    # status_text.config(text=f'Metadata for {song_name} added')

def add_song(event):
    inp_song = inpBox.get()
    inpBox.delete(0, 'end')
    song_names.append(inp_song)
    # status_text.delete('1.0', '100.100')
    # status_text.insert('1.0', str(song_names))

inpBox.bind("<Return>", add_song)

def add_album():
    # find album by name
    album = inpBox.get()
    inpBox.delete(0, 'end')
    results = sp1.search(q="album:" + album, type="album")

    # get the first album uri
    album_id = results['albums']['items'][0]['uri']

    # get album tracks
    tracks = sp1.album_tracks(album_id)
    for track in tracks['items']:
        name = track['name']
        song_names.append(name)

    # status_text.delete('1.0', '100.100')
    # status_text.insert('1.0', str(song_names))

btn_album = tkinter.Button(window, text="Add Album", command=add_album)
btn_album.place(relwidth=0.2, relheight=0.05, rely=0.1, relx=0.4)


def start_downloads():
    if len(song_names) > 0:
        start = time.perf_counter()


        for song_name in song_names:
            append_video_link(song_name)

        for link, song_name in zip(links, song_names):
            file_path, artist_name, album, song, year = get_song_info(song_name)
            download_video_link(link, file_path, artist_name, album, song, year)


        status_text.insert('1.0', f'Done, this took {time.perf_counter() - start} seconds\n')
        song_names.clear()


btn_done = tkinter.Button(window, text="Start downloads", command=start_downloads)
btn_done.place(relwidth=0.2, relheight=0.05, rely=0.175, relx=0.4)
window.mainloop()


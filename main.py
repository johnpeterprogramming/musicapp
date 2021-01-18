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

import tkinter
from tkinter import ttk

window = tkinter.Tk()

window.geometry("600x600")

window.title("Music Downloader")

caption = tkinter.Label(window, text="Add songs or album to be downloaded", font=("Arial Bold", 16))
caption.grid(column=0, row=0)

status_text = tkinter.Text(window, font=("Arial", 10))

status_text.grid(column=0, row=5)

inpBox = tkinter.Entry(window,width=30)
inpBox.grid(column=0, row=1)

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
    status_text.insert('1.0', f'Getting link for {name}\n')


    try:
        link = 'https://www.youtube.com/results?search_query=' + name + '+' + get_song_info(name)[1]

        browser.get(link)

        soup = BeautifulSoup(browser.page_source, features="lxml")

        first_video_link = soup.find(id='video-title')

        links.append('https://www.youtube.com' + first_video_link['href'])
    except:
        print(f'{name} couldnt be found')

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

    print('Starting Download')
    stream.download(location)
    print('Finished Download, adding metadata')

    audio = AudioSegment.from_file(os.path.join(location, stream.default_filename))

    audio.export(os.path.join(location, song_name.replace(' ', '_'))+'.mp3', format='mp3', tags={'albumartist':artist_name,'album':album_name, 'artist':artist_name, 'title':song_name, 'year':release_date})

    os.remove(os.path.join(location, stream.default_filename))

    status_text.insert('1.0', f'{song_name} downloaded\n')

def add_song(event):
    inp_song = inpBox.get()
    inpBox.delete(0, 'end')
    song_names.append(inp_song)
    status_text.delete('1.0', '100.100')
    status_text.insert('1.0', str(song_names))

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
        
    status_text.delete('1.0', '100.100')
    status_text.insert('1.0', str(song_names))


btn_album = tkinter.Button(window, text="Add Album", command=add_album)
btn_album.grid(column=0, row=3)

threads = []

#os.path.normpath()
#os.path.join()
def done():
    print("Downloading")
    if __name__ == '__main__':
        popup = tkinter.Toplevel()
        tkinter.Label(popup, text="Files being downloaded").grid(row=0, column=0)

        progress = 0
        progress_var = tkinter.DoubleVar()
        progress_bar = ttk.Progressbar(popup, variable=progress_var, maximum=100)
        progress_bar.grid(row=1, column=0)  # .pack(fill=tk.X, expand=1, side=tk.BOTTOM)
        popup.pack_slaves()

        progress_step = float(100.0 / (len(song_names)*2))

        start = time.perf_counter()

        for song_name in song_names:
            popup.update()
            append_video_link(song_name)
            progress += progress_step
            progress_var.set(progress)

        browser.close()

        for link, song_name in zip(links, song_names):
            popup.update()
            file_path, artist_name, album, song, year = get_song_info(song_name)
            download_video_link(link, file_path, artist_name, album, song, year)
            progress += progress_step
            progress_var.set(progress)

        status_text.insert('1.0', f'Done, this took {start} seconds\n')
        popup.destroy()


btn_done = tkinter.Button(window, text="Start downloads", command=done)
btn_done.grid(column=0, row=4)
window.mainloop()


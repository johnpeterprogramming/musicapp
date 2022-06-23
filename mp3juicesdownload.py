#Spotify api
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#used to get the first youtube video link from search result
from bs4 import BeautifulSoup, element
import time
import os
import re # for punctuation filtering

#youtube's html is mostly rendered through javascript so I cant use a simple get request i have to render it with selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.firefox import options
import tkinter
import music_tag
import requests

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

options = options.Options()
#options.headless = True

browser = webdriver.Firefox(options=options, executable_path="/home/johna/coding/python/musicapp/geckodriver")

#Initialise spotipy variables
#REPLACE WITH .ENV LATER
client_id = 'e28b2678f2ce4edc9f3e1b2b52588c80'
client_secret = 'd787a0f00e6849a6845384e9a467119b'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp1 = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API

#Initialise downloader variables
song_names = []
links = []

os.chdir('Music')


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

def get_song_link(song_name):
    browser.get('https://www.mp3juices.cc/')
    search_bar = browser.find_element(By.NAME, "query")

    search_bar.send_keys(song_name)

    search_button = browser.find_element(By.ID, "button")
    search_button.click()

    start = time.time()
    while True:
        try:
            download_button = browser.find_element(By.CLASS_NAME, "download")
            break
        except:
            time.sleep(0.5)

        if start - time.time() > 10:
            print("Tried for 10 seconds and now results were found")
            return None

    download_button.click()
        
    start = time.time()
    while True:
        try:
            download_button_button = download_button.find_element(By.XPATH, "/html/body/div/div[2]/div[3]/div[2]/div[2]/a[1]")
            download_link = download_button_button.get_attribute('href')
            print(f"Found link: {download_link}")
            return download_link
        except:
            if time.time() - start > 10:
                print("Couldn't find link for", song_name)
                return False
            time.sleep(0.5)
            print("sleeping looking for download button")

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

#btn_album = tkinter.Button(window, text="Add Album", command=add_album)
#btn_album.place(relwidth=0.2, relheight=0.05, rely=0.1, relx=0.4)

def download_audio_link(link, file_path, artist_name, album, song, year):
    os.makedirs(link)
    r = requests.get(link)
    song_location = os.path.join(file_path, song) 
    with open(song_location, 'wb') as f:
        f.write(r.content)
    print("song has been downloaded, busy adding metadata")
    f = music_tag.load_file(song_location)
    f['album'] = album
    f['artist'] = artist_name
    f['year'] = year
    f['tracktitle'] = song
    f.save()
    print("metadata had been added ")


def start_downloads():
    if len(song_names) > 0:
        start = time.perf_counter()

        for song_name in song_names:
            file_path, artist_name, album, song, year = get_song_info(song_name)
            link = get_song_link(song_name)
            if link:
                download_audio_link(link, file_path, artist_name, album, song, year)

        status_text.insert('1.0', f'Done, this took {time.perf_counter() - start} seconds\n')
        song_names.clear()


btn_done = tkinter.Button(window, text="Start downloads", command=start_downloads)
btn_done.place(relwidth=0.2, relheight=0.05, rely=0.175, relx=0.4)
window.mainloop()


import threading
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

import tkinter
from tkinter import filedialog
from tkinter import ttk

pygame.mixer.init()

window = tkinter.Tk()
window.geometry("560x500")

window.title("Music Downloader")

frame = tkinter.Frame(window, bg='#4C4C4C')
frame.place(relwidth=1, relheight=0.6)

framemp = tkinter.Frame(window, bg='#4C4C4C')
framemp.place(relwidth=1, relheight=0.4, rely=0.6)


caption = tkinter.Label(frame, text="Add songs or album to be downloaded", font=("Arial Bold", 16), bg='#4C4C4C')
caption.place(relx=0.1, relwidth=0.8, relheight=0.05)

status_text = tkinter.Text(frame, font=("Arial", 10), bg='#999191')
status_text.place(relx=0.1, rely=0.4, relwidth=0.8, relheight=0.5)

inpBox = tkinter.Entry(frame,width=30, bg='#999191')
inpBox.place(relx=0.3, rely=0.1, relwidth=0.4, relheight=0.05)

def add_song():
    songdir = filedialog.askopenfilename(initialdir="Music", title="Choose a song", filetypes=(('mp3 files', "*.mp3"), ))
    song = ntpath.basename(songdir)
    song_box.insert('end', song)

def add_multiple_songs():
    songdirs = filedialog.askopenfilenames(initialdir="Music", title="Choose a song", filetypes=(('mp3 files', "*.mp3"),))
    for songdir in songdirs:
        song = ntpath.basename(songdir)
        song_box.insert('end', song)

def remove_song():
    song_box.delete('anchor')
    pygame.mixer.music.stop()

def remove_all_songs():
    song_box.delete(0, 'end')
    pygame.mixer.music.stop()

def play(path = os.getcwd()):
    song = song_box.get("active")
    name = song
    for root, dirs, files in os.walk(path):
        if name in files:
            song_dir = os.path.join(root, name)
    pygame.mixer.music.load(song_dir)
    pygame.mixer.music.play(loops=0)

def stop():
    pygame.mixer.music.stop()
    song_box.selection_clear('active')

global paused
paused = False

def pause(is_paused):
    global paused
    paused = is_paused
    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        pygame.mixer.music.pause()
        paused = True

def next_song():
    next_one = song_box.curselection()
    next_one = next_one[0]+1
    song_box.selection_clear(0, 'end')

    song_box.activate(next_one)
    song_box.selection_set(next_one, last=None)

    play()

def previous_song():
    previous_one = song_box.curselection()
    previous_one = previous_one[0] - 1
    song_box.selection_clear(0, 'end')

    song_box.activate(previous_one)
    song_box.selection_set(previous_one, last=None)

    play()

song_box = tkinter.Listbox(framemp, bg='#999191', selectbackground="black", selectforeground="red")
song_box.place(relx=0.1, rely=0.2, relwidth=0.8, relheight=0.4)

play_btn = tkinter.Button(framemp, text="Play", command=play)
pause_btn = tkinter.Button(framemp, text="Pause", command=lambda :pause(paused))
stop_btn = tkinter.Button(framemp, text="Stop", command=stop)
next_btn = tkinter.Button(framemp, text="Next", command=next_song)
previous_btn = tkinter.Button(framemp, text="Previous", command=previous_song)

play_btn.place(relx=0.2, rely=0.7, relwidth=0.1, relheight=0.1)
pause_btn.place(relx=0.3, rely=0.7, relwidth=0.1, relheight=0.1)
stop_btn.place(relx=0.4, rely=0.7, relwidth=0.1, relheight=0.1)
next_btn.place(relx=0.5, rely=0.7, relwidth=0.1, relheight=0.1)
previous_btn.place(relx=0.6, rely=0.7, relwidth=0.1, relheight=0.1)

menump = tkinter.Menu(window)
window.config(menu=menump)

add_song_menu = tkinter.Menu(menump)
menump.add_cascade(label="Add Songs", menu=add_song_menu)
add_song_menu.add_command(label="Add one song to playlist", command=add_song)
add_song_menu.add_command(label="Add multiple songs to playlist", command=add_multiple_songs)

remove_song_menu = tkinter.Menu(menump)
menump.add_cascade(label="Remove Songs", menu=remove_song_menu)
remove_song_menu.add_command(label="Remove song from playlist", command=remove_song)
remove_song_menu.add_command(label="Remove all songs from playlist", command=remove_all_songs)

def connect():
    global browser
    connection = 0
    success_connect = False
    while connection < 5 and success_connect != True:
        connection = connection + 1
        try:
            options = Options()
            options.headless = True

            browser = webdriver.Firefox(options=options)
            success_connect = True
        except:
            success_connect = False

    if success_connect == False:
        popup1 = tkinter.Toplevel()
        tkinter.Label(popup1, text="Unable to connect").grid(row=0, column=0)

client_id = 'e28b2678f2ce4edc9f3e1b2b52588c80'
client_secret = 'd787a0f00e6849a6845384e9a467119b'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp1 = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API

song_names = []
links = []


home_path = os.getcwd()

if not os.path.exists('Music'):
    os.makedirs('Music')

os.chdir('Music')

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


    album_name = album_name.translate ({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"})
    artist_name = artist_name.translate ({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"})

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

btn_album = tkinter.Button(frame, text="Add Album", command=add_album)
btn_album.place(relx=0.4, rely=0.2, relwidth=0.2, relheight=0.05)

threads = []

#os.path.normpath()
#os.path.join()
def done_thread():
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

def done():
    thr = threading.Thread(target=done_thread, args=[])
    thr.start()

btn_done = tkinter.Button(frame, text="Start downloads", command=done)
btn_done.place(relx=0.4, rely=0.3, relwidth=0.2, relheight=0.05)
connect()
window.mainloop()
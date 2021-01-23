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

from mutagen.mp3 import MP3

from tkinter import messagebox
from tkinter import filedialog
import tkinter
from tkinter import ttk

#Initialising mixer
pygame.mixer.init()

#Define starting setting for window

window = tkinter.Tk()
window.geometry("600x600")
window.title("Music Downloader")

#Create frame for downloader portion
frame = tkinter.Frame(window, bg='#4C4C4C')
frame.place(relwidth=1, relheight=0.6)

#Create mp3 player frame
framemp = tkinter.Frame(window, bg='#4C4C4C')
framemp.place(relwidth=1, relheight=0.4, rely=0.6)

#Create Label, Entry and text box
caption = tkinter.Label(frame, text="Add songs or album to be downloaded", font=("Arial Bold", 16), bg='#4C4C4C', fg='white')
caption.place(relx=0.1, relwidth=0.8, relheight=0.05)

status_text = tkinter.Text(frame, font=("Arial", 10), bg='#999191')
status_text.place(relx=0.1, rely=0.4, relwidth=0.8, relheight=0.5)

inpBox = tkinter.Entry(frame,width=30, bg='#999191')
inpBox.place(relx=0.3, rely=0.1, relwidth=0.4, relheight=0.05)

#Tracks the current amount of time the song has been playing
def play_time(path = os.getcwd()):
    #Kill the function if playback is stopped
    if stopped:
        return

    #Get the current playback time and convert to time format
    current_time = pygame.mixer.music.get_pos() / 1000
    converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))

    #get the currently playing song
    song = song_box.get("active")
    name = song
    #Fetch the currently playing songs directory
    for root, dirs, files in os.walk(path):
        if name in files:
            song_dir = os.path.join(root, name)

    #Get the currently playing songs duration
    song_muta = MP3(song_dir)
    song_length = song_muta.info.length

    #Convert the duration to a time format
    converted_length_time = time.strftime('%M:%S', time.gmtime(song_length))

    #Sync the slider and the variable
    current_time_synced = current_time + 1
    #Change slider and label behaviour based on current song state
    #Check if the song is completed and stop label from continueing count
    if int(progress_slider.get() + 1) == int(song_length):
        duration_lbl.config(text=f'Time Elapsed: {converted_length_time} of {converted_length_time}  ')
        next_song()
    #Ignore updating the slider and label while song is paused
    elif paused:
        pass
    #Check if slider has been moved and if not then update in increments as normal
    elif int(progress_slider.get()) == int(current_time_synced):
        slider_position = int(song_length)
        progress_slider.config(to=slider_position, value=int(current_time_synced))
        duration_lbl.config(text=f'Time Elapsed: {converted_current_time} of {converted_length_time}  ')
    #If slider has been moved update song and label to the current position of slider
    else:
        slider_position = int(song_length)
        progress_slider.config(to=slider_position, value=int(progress_slider.get()))
        converted_current_time = time.strftime('%M:%S', time.gmtime(int(progress_slider.get())))
        duration_lbl.config(text=f'Time Elapsed: {converted_current_time} of {converted_length_time}  ')
        next_time = int(progress_slider.get() + 1)
        progress_slider.config(value=next_time)

    #Make the function call itself every second if not stopped
    duration_lbl.after(1000, play_time)

#add a single song to the playlist
def add_song():
    #Store the file chosen in dialog box to variable
    songdir = filedialog.askopenfilename(initialdir=os.getcwd, title="Choose a song", filetypes=(('mp3 files', "*.mp3"), ))
    #Remove path from file
    song = ntpath.basename(songdir)
    #Add to playlist
    song_box.insert('end', song)

 #add multiple songs to playlist
def add_multiple_songs():
    #Store files chosen in dialog box to a variable
    songdirs = filedialog.askopenfilenames(initialdir=os.getcwd(), title="Choose a song", filetypes=(('mp3 files', "*.mp3"),))
    #Loop through songs removing path and adding to playlist
    for songdir in songdirs:
        song = ntpath.basename(songdir)
        song_box.insert('end', song)

#Remove a song from the playlist
def remove_song():
    #Stop the song if it is playing
    stop()
    #Remove song from playlist
    song_box.delete('anchor')

#Remove all the songs from the playlist
def remove_all_songs():
    #Stop any songs currently playing
    stop()
    #Clear the playlist
    song_box.delete(0, 'end')

#Play the currently selected song
def play(path = os.getcwd()):
    #Reset label and progress slider
    progress_slider.config(value=0)
    duration_lbl.config(text='')
    #Make sure play_time function terminates before starting a new one
    #This code looks redundant, but it is required
    global stopped
    stopped =True
    #Retrieve the selected song
    song = song_box.get("active")
    name = song
    #Grab the songs directory
    for root, dirs, files in os.walk(path):
        if name in files:
            song_dir = os.path.join(root, name)
    #Load the song and play it
    stopped = False
    pygame.mixer.music.load(song_dir)
    pygame.mixer.music.play(loops=0)
    #Being updating UI elements
    play_time()

# Set the default value for stopped
global stopped
stopped = False

#Stops the currently playing song
def stop():
    #Reset Slider and label
    progress_slider.config(value=0)
    duration_lbl.config(text='')
    #Stop the currently playing song
    pygame.mixer.music.stop()
    #Clear the current selection in the playlist
    song_box.selection_clear('active')
    #Set stopped to true, to terminate play_time function
    global stopped
    stopped = True

#Set default value for paused
global paused
paused = False

#Pause the currently playing song
def pause(is_paused):
    #Import the paused variable and update it
    global paused
    paused = is_paused
    #Check if song is paused then unpause it
    if paused:
        pygame.mixer.music.unpause()
        paused = False
    #if not paused then pause it
    else:
        pygame.mixer.music.pause()
        paused = True

#Select and play the next song
def next_song():
    global stopped
    stopped = True
    #Reset slider and label
    progress_slider.config(value=0)
    duration_lbl.config(text='')
    #Get the current selection
    next_one = song_box.curselection()
    #Update to the next selection
    try:
        next_one = next_one[0]+1
    except:
        next_one = 0
    #Clear the current selection
    song_box.selection_clear(0, 'end')
    #Update the selection on playlist
    song_box.activate(next_one)
    song_box.selection_set(next_one, last=None)
    #Play the newly selected song
    window.after(1000, play)

#Select and play the previous song
def previous_song():
    global stopped
    stopped = True
    #Reset slider and label
    progress_slider.config(value=0)
    duration_lbl.config(text='')
    #Get the current selection
    previous_one = song_box.curselection()
    #Update to the previous selection
    previous_one = previous_one[0] - 1
    #Clear the current selection on playlist
    song_box.selection_clear(0, 'end')
    #Update to previous selection on playlist
    song_box.activate(previous_one)
    song_box.selection_set(previous_one, last=None)
    #Play the newly selected song
    window.after(1000, play)

#Updates song position when slider is moved
def slide(event, path=os.getcwd()):
    #Get the currently selected song
    global stopped
    stopped = True
    song = song_box.get("active")
    name = song
    #Get the currently selected song's directory
    for root, dirs, files in os.walk(path):
        if name in files:
            song_dir = os.path.join(root, name)
    #Load and play from the postion of slider
    stopped = False
    pygame.mixer.music.load(song_dir)
    pygame.mixer.music.play(loops=0, start= int(progress_slider.get()))

#Change the volume
def volume(event):
    #Update volume to position of slider
    pygame.mixer.music.set_volume(volume_slider.get())

#Create playlist Listbox
song_box = tkinter.Listbox(framemp, bg='#999191', selectbackground="black", selectforeground="red")
song_box.place(relx=0.1, rely=0.2, relwidth=0.7, relheight=0.4)

#Create all the mp3 player's buttons
play_btn = tkinter.Button(framemp, text="Play", command=play)
pause_btn = tkinter.Button(framemp, text="Pause", command=lambda :pause(paused))
stop_btn = tkinter.Button(framemp, text="Stop", command=stop)
next_btn = tkinter.Button(framemp, text="Next", command=next_song)
previous_btn = tkinter.Button(framemp, text="Previous", command=previous_song)

play_btn.place(relx=0.2, rely=0.65, relwidth=0.1, relheight=0.1)
pause_btn.place(relx=0.3, rely=0.65, relwidth=0.1, relheight=0.1)
stop_btn.place(relx=0.4, rely=0.65, relwidth=0.1, relheight=0.1)
next_btn.place(relx=0.6, rely=0.65, relwidth=0.1, relheight=0.1)
previous_btn.place(relx=0.7, rely=0.65, relwidth=0.1, relheight=0.1)

#Define the menu bar
menump = tkinter.Menu(window)
window.config(menu=menump)

#Add menu's to the menu bar
add_song_menu = tkinter.Menu(menump)
menump.add_cascade(label="Add Songs", menu=add_song_menu)
add_song_menu.add_command(label="Add one song to playlist", command=add_song)
add_song_menu.add_command(label="Add multiple songs to playlist", command=add_multiple_songs)

remove_song_menu = tkinter.Menu(menump)
menump.add_cascade(label="Remove Songs", menu=remove_song_menu)
remove_song_menu.add_command(label="Remove song from playlist", command=remove_song)
remove_song_menu.add_command(label="Remove all songs from playlist", command=remove_all_songs)

#Create label and slider for tracking durationg of song
duration_lbl = tkinter.Label(framemp, text='', bd=1, relief="groove", anchor='e', bg='#999191')
duration_lbl.place(rely=0.9, relwidth=1, relheight=0.1)

progress_slider = ttk.Scale(framemp, from_=0, to=100, orient='horizontal', value=0, command=slide)
progress_slider.place(rely=0.8, relheight=0.1, relwidth=1)

#Create volume slider and the labeled frame for it
volume_frame = tkinter.LabelFrame(framemp, text="Volume")
volume_frame.place(rely=0.2, relheight=0.4, relwidth=0.1, relx=0.8)

volume_slider = ttk.Scale(volume_frame, from_=1, to=0, orient='vertical', value=1, command=volume)
volume_slider.place(relheight=1, relwidth=1)

def connect():
    #Initialize variables
    global browser
    connection = 0
    success_connect = False
    #Loops runs 5 times or until there is a connection
    while connection < 5 and success_connect != True:
        #Add 1 to attempt counter
        connection = connection + 1
        #Try to connect
        try:
            options = Options()
            options.headless = True

            browser = webdriver.Firefox(options=options)
            #If connection succeeds it will reach this line of code breaking the loop
            success_connect = True
        except:
            #If connection does not succeed it will try again, unless connection=5
            success_connect = False
    #If all 5 attempts failed alert the user that it was unable to connect
    if success_connect == False:
        popup1 = tkinter.Toplevel()
        tkinter.Label(popup1, text="Unable to connect").grid(row=0, column=0)

#Initialise spotipy variables
client_id = 'e28b2678f2ce4edc9f3e1b2b52588c80'
client_secret = 'd787a0f00e6849a6845384e9a467119b'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp1 = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API

#Initialise downloader variables
global song_names
song_names = []
global links
links = []

#Make sure the Music folder exists
if os.path.exists('Music'):
    #if it does then change working directory to it
    os.chdir('Music')
else:
    #if it does not create it then change working directory to it
    os.makedirs('Music')
    os.chdir('Music')

#Save the current working directory to variable
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
btn_album.place(relwidth=0.2, relheight=0.05, rely=0.1, relx=0.4)

threads = []

def clear_list():
    global song_names
    song_names = []
    status_text.delete('1.0', '100.100')
    status_text.insert('1.0', str(song_names))

btn_clear = tkinter.Button(window, text="Clear List", command=clear_list)
btn_clear.place(relwidth=0.2, relheight=0.025, rely=0.525, relx=0.7)

#os.path.normpath()
#os.path.join()
def done_thread():
    global song_names
    global links
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


        for link, song_name in zip(links, song_names):
            popup.update()
            file_path, artist_name, album, song, year = get_song_info(song_name)
            download_video_link(link, file_path, artist_name, album, song, year)
            progress += progress_step
            progress_var.set(progress)

        status_text.insert('1.0', f'Done, this took {start} seconds\n')
        song_names = []
        links = []
        popup.destroy()


#Start the downloads thread
def done():
    #Set the threads target function
    thr = threading.Thread(target=done_thread, args=[])
    #Start the thread. Will self terminate once function is completed
    thr.start()

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        browser.close()
        window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)

btn_done = tkinter.Button(window, text="Start downloads", command=done)
btn_done.place(relwidth=0.2, relheight=0.05, rely=0.175, relx=0.4)
connect()
window.mainloop()
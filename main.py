import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from mp3_tagger import MP3File
from mp3_tagger import VERSION_BOTH

#checks for system OS because directories differ
from platform import system
print(f'You are running the {system()} Operating System bro')


# This opens a window in the background(headless) so it's faster and doesn't bother the user
options = Options()
options.headless = True

browser = webdriver.Firefox(options=options)

from pytube import YouTube

import os
#Your mom is redundent

client_id = 'e28b2678f2ce4edc9f3e1b2b52588c80'
client_secret = 'd787a0f00e6849a6845384e9a467119b'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp1 = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API

def tag_mp3(path_to_mp3,album,artist,song):
    #Open the file
    mp3 = MP3File(path_to_mp3)
    #Set tags
    mp3.album = album
    mp3.artist = artist
    mp3.song = song
    #Save and close the file
    mp3.save()
    #View tags
    tags = mp3.get_tags()
    print(tags)

def set_download_path(name):
    #change directory to the directory of the script
    abspath = os.path.abspath(__file__)
    print('abspath', abspath)  
    dname = os.path.dirname(abspath)
    print('dname', dname)
    os.chdir(dname)
    #get track data
    result = sp1.search(name)
    track = result['tracks']['items'][0]
    #get artist data and display artist data
    artist = sp1.artist(track["artists"][0]["external_urls"]["spotify"])
    print("artist genres:", artist["genres"])
    print("artist:", artist["name"])
    #get album data and display album data
    album = sp1.album(track["album"]["external_urls"]["spotify"])
    print("album genres:", album["genres"])
    print("album release-date:", album["release_date"])
    print("album:", album["name"])

    #assigning variables to replace special characters
    album_name = album["name"]
    artist_name = artist["name"]

    #no need for if statements because python won't return error if theres nothing to replace
    #I know theres a more efficient way to remove punctuation, I'll do it later
    album_name = album_name.replace('?', '')
    album_name = album_name.replace('!', '')
    album_name = album_name.replace(':', '')

    artist_name = artist_name.replace('?', '')
    artist_name = artist_name.replace('!', '')
    artist_name = artist_name.replace(':', '')

    #check if directory for artist and album exists else create directory for them
    if system == 'Windows':
        does_dir_exist = os.path.exists(fr"Music\{artist_name}\{album_name}")
        if not does_dir_exist:
            os.makedirs(fr"Music\{artist_name}\{album_name}")
        os.chdir(fr"Music\{artist_name}\{album_name}")
    else:
        does_dir_exist = os.path.exists(f"Music/{artist_name}/{album_name}")
        if not does_dir_exist:
            os.makedirs(f"Music/{artist_name}/{album_name}")
        os.chdir(f"Music/{artist_name}/{album_name}")
    class metadata:
        def __init__(self):
            metadata.artist = artist_name
            metadata.album = album_name
            metadata.song = name

    return metadata()

def get_video_link(name):
    link = 'https://www.youtube.com/results?search_query=' + name.replace(' ', '+')

    browser.get(link)

    soup = BeautifulSoup(browser.page_source, features="lxml")

    first_video_link = soup.find(id='video-title')
    if first_video_link:
        return 'https://www.youtube.com'+first_video_link['href']
    else:
        return None

def download_video_link(link,name):
    if link:
        yt = YouTube(link)
        filtered = yt.streams.filter(only_audio=True)

        stream = filtered[0]
        print('Starting Download')
        stream.download()
        os.rename(stream.default_filename, f'{name}.mp3')
        print('Finished')
    else:
        print('No Video Found')

#Selection code. Will replace with GUI after main functionality completed
print('(1) Song (One)')
print('(2) Songs (Several)')
print('(3) Album')

options = int(input('> '))

if options == 1:
    name = input('Name of Song: ')
    data = set_download_path(name)
    video_link = get_video_link(name)
    download_video_link(video_link,name)
    if system == 'Windows':
        tag_mp3(os.getcwd() + '\\' + name + '.mp3',data.album,data.artist,data.song)
    else:
        tag_mp3(os.getcwd() + '/' + name + '.mp3', data.album, data.artist, data.song)
    browser.close()

elif options == 2:
    print('Under construction')

elif options == 3:
    # find album by name
    album = input("Name of album:")
    results = sp1.search(q="album:" + album, type="album")

    # get the first album uri
    album_id = results['albums']['items'][0]['uri']

    # get album tracks
    tracks = sp1.album_tracks(album_id)
    for track in tracks['items']:
        name = track['name']
        data = set_download_path(name)
        video_link = get_video_link(name)
        download_video_link(video_link,name)
        if system == 'Windows':
            tag_mp3(os.getcwd() + '\\' + name + '.mp3', data.album, data.artist, data.song)
        else:
            tag_mp3(os.getcwd() + '/' + name + '.mp3', data.album, data.artist, data.song)
    browser.close()

else:
    print("We didn't understand")

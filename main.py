import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

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


# We have to turn this into two functions later
# get_video_link(name) returns the link of the youtube video with that search result
# download_video(link, location) downloads the youtube video link at a certain location
# the reason there should be two functions is because it takes the longest to actually get the link so we can use multiprocessing to improve efficiency
def download_video(name):
    if name+'.mp3' not in os.listdir():
        link = 'https://www.youtube.com/results?search_query=' + name.replace(' ', '+')

        browser.get(link)

        soup = BeautifulSoup(browser.page_source, features="lxml")

        first_video_link = soup.find(id='video-title')
        if first_video_link:
            youtube_link = 'https://www.youtube.com'+first_video_link['href']
            print(youtube_link)
            yt = YouTube(youtube_link)
            filtered = yt.streams.filter(only_audio=True)

            stream = filtered[0]
            print('Starting Download')
            stream.download()
            os.rename(stream.default_filename, stream.default_filename.replace('.mp4', '.mp3'))
            print('Finished')


            try:
                os.rename(name+'.mp4', name + '.mp3')
                
            except:
                print("couldn't rename")#fixed a typo
                #I'm really offended (anger)
                print(f'file: ' + name + '.mp4')
                print('to: ' + name + '.mp3')
        else:
            print('not found')
    else:
        print(f'{name} already downloaded')

#Selection code. Will replace with GUI after main functionality completed
print('(1) Song')
print('(2) Album')
print('(3) Sync Spotify account')

options = int(input('> '))

if options == 1:
    name = input('Name of Song: ')
    set_download_path(name)
    download_video(name)
    browser.close()

elif options == 2:
    # find album by name
    album = input("Name of album:")
    results = sp1.search(q="album:" + album, type="album")

    # get the first album uri
    album_id = results['albums']['items'][0]['uri']

    # get album tracks
    tracks = sp1.album_tracks(album_id)
    for track in tracks['items']:
        name = track['name']
        set_download_path(name)
        download_video(name)
    browser.close()

'''
elif options == 3:

    print('Getting token for spotify api')
    print('Gottem')

    sp = spotipy.Spotify(auth=token)
    print('Getting user saved tracks')
    results = sp.current_user_saved_tracks()

    for item in results['items']:
        name = item['track']['name']
        print('Finding ' + name)
        set_download_path(name) #added sorting function to loop
        download_video(name)
'''

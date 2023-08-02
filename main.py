from bs4 import BeautifulSoup
import requests

import spotipy
from spotipy.oauth2 import SpotifyOAuth

TOP_100_URL = "https://www.billboard.com/charts/hot-100"

SPOTIFY_CLIENT_ID = ""
SPOTIFY_CLIENT_SECRET = ""
REDIRECT_URL = "http://example.com/"


# -------------------------- scraping Billboards website ---------------------------- #


user_input_date = input("From what time would you like to have your flashback playlist from? \n"
                        "(answer in YYYY-MM-DD format): ")

user_year = user_input_date.split("-")[0]
print(user_input_date)

response = requests.get(f"{TOP_100_URL}/{user_input_date}")
soup = BeautifulSoup(response.text, "html.parser")


# --------------- this was my way ---------------------- #
first_list_item = soup.find(name="ul", class_="lrv-a-unstyle-list lrv-u-flex lrv-u-height-100p "
                                              "lrv-u-flex-direction-column@mobile-max").text
first_song = first_list_item.strip().split()[0]

song_titles = soup.find_all(name="h3", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021"
                                              " lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 "
                                              "u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 "
                                              "u-max-width-230@tablet-only")
all_100_songs = [song.text.strip() for song in song_titles]
all_100_songs.insert(0, first_song)

print(all_100_songs)


# --------------- but this is way nicer ---------------- #

list_items = soup.select("li ul li h3")
all_100_songs_2 = [song.text.strip() for song in list_items]
print(all_100_songs_2)


# --------------------------------------- Spotify ------------------------------------- #

# import spotipy
# from spotipy.oauth2 import SpotifyOAuth

scope = "playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,
                                               client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URL))
spotify_user_id = sp.current_user()["id"]


# ------------------ searching for spotify track uri ---------------------- #

uri = []
for song in all_100_songs_2:
    search_result = sp.search(q=f"track:{song} year:{user_year}", type="track")

    try:
        uri.append(search_result["tracks"]["items"][0]["uri"])
        print("song appended to list\n")
    except IndexError:
        print(f"no result found for {song}\n")

print(uri)

# ----------------------- creating the playlist and adding the songs ----------------------- #

playlist = sp.user_playlist_create(user=spotify_user_id,
                                   name=f"{user_input_date} 100 Playlist",
                                   public=False,
                                   description="Take me back in time with these charts")


print("playlist set up")


sp.playlist_add_items(playlist_id=playlist["id"], items=uri, position=None)

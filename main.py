from bs4 import BeautifulSoup
from dotenv import dotenv_values
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

config = dotenv_values(".env")
client_id = config["ClientID"]
client_secret = config["ClientSecret"]
redirect_url = config["RedirectUrl"]
username = config["username"]
UserAgent = config["UserAgent"]

target_date = input("Choisis une date (format : YYYY-MM-DD) : ")


header = {"User-Agent": UserAgent}
billboard_url = "https://www.billboard.com/charts/hot-100/" + target_date
response = requests.get(url=billboard_url, headers=header)

soup = BeautifulSoup(response.text, 'html.parser')
song_names_raw = soup.select("li ul li h3")
song_names = [song.getText().strip() for song in song_names_raw]

# Auth spotify
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=redirect_url,
        client_id=client_id,
        client_secret=client_secret,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]
print(user_id)

# Cherche sur spotify les musiques correspondant aux noms dans "song_names"
song_uris = []
year = target_date.split("-")[0]
song_score = 0
for song in song_names:
    song_score +=1
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(f'{song_score}%')
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} n'existe pas sur spotify.")

# Créer une playlist
playlist = sp.user_playlist_create(user=user_id, name=f"{target_date} Billboard 100", public=False)
print(playlist)

# Assigne les sons dans la playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

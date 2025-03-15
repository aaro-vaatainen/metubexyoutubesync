import os
import time
import json
import requests
from pytube import Playlist

# Konfiguraatio ympäristömuuttujista
PLAYLIST_FILE = os.getenv("PLAYLIST_FILE", "playlists.json")
DESTINATION_URL = os.getenv("DESTINATION_URL", "https://example.url/add")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))  # Oletuksena 5 min
DB_FILE = "downloaded_videos.json"

# Lataa soittolistatiedostosta
def load_playlists():
    if not os.path.exists(PLAYLIST_FILE):
        print(f"Virhe: {PLAYLIST_FILE} ei löydy.")
        return []
    
    try:
        with open(PLAYLIST_FILE, "r") as f:
            if PLAYLIST_FILE.endswith(".json"):
                return json.load(f)
            else:
                return [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"Virhe ladattaessa soittolistaa: {e}")
        return []

# Lataa aiemmin ladatut videot
def load_downloaded_videos():
    try:
        with open(DB_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

# Tallenna ladatut videot
def save_downloaded_videos(video_ids):
    with open(DB_FILE, "w") as f:
        json.dump(list(video_ids), f)

# Hae soittolistan videot
def get_playlist_videos(playlist_url):
    try:
        return {video.video_id for video in Playlist(playlist_url).videos}
    except Exception as e:
        print(f"Virhe haettaessa soittolistaa {playlist_url}: {e}")
        return set()

# Lähetä latauspyyntö MeTubeen
def download_video(video_url):
    data = {
        "url": video_url,
        "quality": "best",
        "format": "any",
        "playlist_strict_mode": False,
        "auto_start": True
    }
    response = requests.post(DESTINATION_URL, json=data)
    return response.status_code == 200

if __name__ == "__main__":
    downloaded_videos = load_downloaded_videos()

    while True:
        playlists = load_playlists()
        for playlist_url in playlists:
            print(f"Tarkistetaan soittolista: {playlist_url}")
            playlist_videos = get_playlist_videos(playlist_url)
            new_videos = playlist_videos - downloaded_videos

            for video_id in new_videos:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                if download_video(video_url):
                    print(f"Ladattu: {video_url}")
                    downloaded_videos.add(video_id)
                    save_downloaded_videos(downloaded_videos)
                else:
                    print(f"Virhe ladattaessa: {video_url}")

        print(f"Odotetaan {CHECK_INTERVAL} sekuntia...")
        time.sleep(CHECK_INTERVAL)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

PIPED_API = "https://pipedapi.kavin.rocks"

@app.post("/search")
def search_song(req: SearchRequest):
    try:
        # Search for the song
        search_resp = requests.get(
            f"{PIPED_API}/search",
            params={"q": req.query, "filter": "music_songs"},
            timeout=15
        )
        search_data = search_resp.json()
        items = search_data.get("items", [])

        if not items:
            return {"error": "No results found", "stream_url": None}

        video = items[0]
        video_id = video["url"].replace("/watch?v=", "")
        title = video.get("title", req.query)
        artist = video.get("uploaderName", "")
        thumbnail = video.get("thumbnail", "")

        # Get stream URL
        stream_resp = requests.get(
            f"{PIPED_API}/streams/{video_id}",
            timeout=15
        )
        stream_data = stream_resp.json()

        # Get best audio stream
        audio_streams = stream_data.get("audioStreams", [])
        stream_url = None

        for stream in audio_streams:
            if stream.get("mimeType", "").startswith("audio/"):
                stream_url = stream["url"]
                break

        if not stream_url and audio_streams:
            stream_url = audio_streams[0]["url"]

        return {
            "stream_url": stream_url,
            "title": title,
            "artist": artist,
            "thumbnail": thumbnail,
            "duration": video.get("duration", 0)
        }

    except Exception as e:
        return {"error": str(e), "stream_url": None}

@app.get("/")
def root():
    return {"status": "SaveGram backend running!"}

@app.head("/")
def root_head():
    return {}
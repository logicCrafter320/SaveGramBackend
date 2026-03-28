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

PIPED_INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://piped-api.garudalinux.org",
    "https://api.piped.projectsegfau.lt",
]

@app.post("/search")
def search_song(req: SearchRequest):
    for PIPED_API in PIPED_INSTANCES:
        try:
            search_resp = requests.get(
                f"{PIPED_API}/search",
                params={"q": req.query, "filter": "music_songs"},
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            
            if search_resp.status_code != 200:
                continue
                
            search_data = search_resp.json()
            items = search_data.get("items", [])

            if not items:
                continue

            video = items[0]
            video_id = video["url"].replace("/watch?v=", "")
            title = video.get("title", req.query)
            artist = video.get("uploaderName", "")
            thumbnail = video.get("thumbnail", "")

            stream_resp = requests.get(
                f"{PIPED_API}/streams/{video_id}",
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            
            if stream_resp.status_code != 200:
                continue
                
            stream_data = stream_resp.json()
            audio_streams = stream_data.get("audioStreams", [])
            stream_url = None

            for stream in sorted(audio_streams, key=lambda x: x.get("bitrate", 0), reverse=True):
                if "audio" in stream.get("mimeType", ""):
                    stream_url = stream["url"]
                    break

            if not stream_url and audio_streams:
                stream_url = audio_streams[0]["url"]

            if stream_url:
                return {
                    "stream_url": stream_url,
                    "title": title,
                    "artist": artist,
                    "thumbnail": thumbnail,
                    "duration": video.get("duration", 0)
                }

        except Exception as e:
            continue

    return {"error": "All sources failed", "stream_url": None}

@app.get("/")
def root():
    return {"status": "SaveGram backend running!"}

@app.head("/")
def root_head():
    return {}
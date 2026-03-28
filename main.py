from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

@app.post("/search")
def search_song(req: SearchRequest):
    try:
        cookie_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
        
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "noplaylist": True,
            "default_search": "ytsearch1",
            "extract_flat": False,
            "cookiefile": cookie_file if os.path.exists(cookie_file) else None,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.query, download=False)

            if "entries" in info:
                info = info["entries"][0]

            stream_url = None
            for fmt in info.get("formats", []):
                if fmt.get("acodec") != "none" and fmt.get("vcodec") == "none":
                    stream_url = fmt["url"]
                    break

            if not stream_url:
                for fmt in info.get("formats", []):
                    if fmt.get("acodec") != "none":
                        stream_url = fmt["url"]
                        break

            title  = info.get("title", req.query)
            artist = info.get("uploader", "")

            if " - Topic" in artist:
                artist = artist.replace(" - Topic", "")

            return {
                "stream_url": stream_url,
                "title": title,
                "artist": artist,
                "duration": info.get("duration", 0),
                "thumbnail": info.get("thumbnail", "")
            }

    except Exception as e:
        return {"error": str(e), "stream_url": None}

@app.get("/")
def root():
    return {"status": "SaveGram backend running!"}

@app.head("/")
def root_head():
    return {}
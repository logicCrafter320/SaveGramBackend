from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

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
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "noplaylist": True,
            "default_search": "ytsearch1",
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.query, download=False)

            # If it's a search result, get first item
            if "entries" in info:
                info = info["entries"][0]

            # Get best audio URL
            stream_url = None
            for fmt in info.get("formats", []):
                if fmt.get("acodec") != "none" and fmt.get("vcodec") == "none":
                    stream_url = fmt["url"]
                    break

            # Fallback to any format with audio
            if not stream_url:
                for fmt in info.get("formats", []):
                    if fmt.get("acodec") != "none":
                        stream_url = fmt["url"]
                        break

            title  = info.get("title", req.query)
            artist = info.get("uploader", "")

            # Clean up artist name
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
ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "default_search": "ytsearch1",
    "extract_flat": False,
    "cookiefile": "cookies.txt",
}
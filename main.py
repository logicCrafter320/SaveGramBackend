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

@app.post("/search")
def search_song(req: SearchRequest):
    try:
        search_resp = requests.get(
            "https://jiosaavn-api-privatecvc2.vercel.app/api/search/songs",
            params={"query": req.query, "page": 1, "limit": 1},
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        raw = search_resp.json()
        
        # Handle different response structures
        if isinstance(raw.get("data"), dict):
            results = raw["data"].get("results", [])
        elif isinstance(raw.get("data"), list):
            results = raw["data"]
        else:
            results = []

        if not results:
            return {"error": "No results found", "stream_url": None}

        song = results[0]
        title = song.get("name", "") or song.get("title", req.query)
        
        artists = song.get("artists", {})
        if isinstance(artists, dict):
            primary = artists.get("primary", [])
            artist = ", ".join([a.get("name", "") for a in primary]) if primary else ""
        else:
            artist = str(artists)

        images = song.get("image", [])
        if images and isinstance(images, list):
            thumbnail = images[-1].get("link", "") or images[-1].get("url", "")
        else:
            thumbnail = ""

        download_urls = song.get("downloadUrl", []) or song.get("download_url", [])
        stream_url = None
        if isinstance(download_urls, list):
            for url_info in reversed(download_urls):
                link = url_info.get("link") or url_info.get("url")
                if link:
                    stream_url = link
                    break

        return {
            "stream_url": stream_url,
            "title": title,
            "artist": artist,
            "thumbnail": thumbnail,
            "duration": song.get("duration", 0)
        }

    except Exception as e:
        return {"error": str(e), "stream_url": None}

@app.get("/")
def root():
    return {"status": "SaveGram backend running!"}

@app.head("/")
def root_head():
    return {}
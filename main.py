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
            "https://saavn.dev/api/search/songs",
            params={"query": req.query, "limit": 1},
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        
        data = search_resp.json()
        results = data.get("data", {}).get("results", [])
        
        if not results:
            return {"error": "No results found", "stream_url": None}
        
        song = results[0]
        title = song.get("name", req.query)
        artist = song.get("artists", {}).get("primary", [{}])[0].get("name", "")
        
        # Get highest quality download URL
        download_urls = song.get("downloadUrl", [])
        stream_url = None
        
        for url_info in reversed(download_urls):
            if url_info.get("url"):
                stream_url = url_info["url"]
                break
        
        # Get thumbnail
        images = song.get("image", [])
        thumbnail = images[-1].get("url", "") if images else ""
        duration = song.get("duration", 0)

        return {
            "stream_url": stream_url,
            "title": title,
            "artist": artist,
            "thumbnail": thumbnail,
            "duration": duration
        }

    except Exception as e:
        return {"error": str(e), "stream_url": None}

@app.get("/")
def root():
    return {"status": "SaveGram backend running!"}

@app.head("/")
def root_head():
    return {}
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from .models import UserProfile, Recommendation
from .engine import get_recommendations, fetch_real_gyms_from_osm
from .data import MOCK_GYMS
import os

app = FastAPI(title="Gym Recommendation System (OSM Powered)")

@app.post("/recommend", response_model=List[Recommendation])
async def recommend_gyms(user: UserProfile):
    # Try fetching real data from OSM
    real_gyms = await fetch_real_gyms_from_osm(
        user.preferred_location[0], 
        user.preferred_location[1],
        user.max_travel_distance_km
    )
    
    # Merge with mock data if OSM returns few results, or just use real
    all_gyms = real_gyms if real_gyms else MOCK_GYMS
    return get_recommendations(user, all_gyms)

# Serve static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def read_index():
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to the Gym Recommendation API"}

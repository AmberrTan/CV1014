from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from .models import UserProfile, Recommendation, UserLocationProfile
from .engine import get_recommendations, fetch_real_gyms_from_osm, ensure_minimum_gyms, user_has_hard_filters
from .data import MOCK_GYMS
from .profile_store import save_profile, get_profile
import os
import logging

root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

app = FastAPI(title="Gym Recommendation System (OSM Powered)")

@app.post("/recommend", response_model=List[Recommendation])
async def recommend_gyms(user: UserProfile):
    # Try fetching real data from OSM
    real_gyms = await fetch_real_gyms_from_osm(
        user.preferred_location[0], 
        user.preferred_location[1],
        user.max_travel_distance_km,
        user=user,
    )
    
    all_gyms = real_gyms if real_gyms else []
    if user_has_hard_filters(user):
        all_gyms = all_gyms + MOCK_GYMS
        return get_recommendations(user, all_gyms)

    # Merge with mock/synthetic data if OSM returns few results
    all_gyms = ensure_minimum_gyms(user, all_gyms)
    return get_recommendations(user, all_gyms)


@app.post("/profile", response_model=UserLocationProfile)
async def save_user_profile(profile: UserLocationProfile):
    save_profile(profile)
    return profile


@app.get("/profile")
async def read_profile_page():
    profile_path = os.path.join(static_path, "profile.html")
    if os.path.exists(profile_path):
        return FileResponse(profile_path)
    return {"message": "Profile page not found"}


@app.get("/profile/{user_id}", response_model=UserLocationProfile)
async def read_user_profile(user_id: str):
    profile = get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

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

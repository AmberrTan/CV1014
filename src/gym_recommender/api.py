from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from gym_recommender.api_models import CompareRequest, GymPayload, RecommendationRequest, SearchRequest
from gym_recommender.services import (
    compare_gym_records,
    create_gym_record,
    get_gym_by_id,
    list_gyms,
    recommend_gym_records,
    search_gym_records,
    serialize_gym,
    update_gym_record,
)

app = FastAPI(title="Gym Recommendation API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/gyms")
def get_gyms() -> list[dict[str, object]]:
    return [serialize_gym(gym) for gym in list_gyms()]


@app.get("/api/gyms/{gym_id}")
def get_gym(gym_id: int) -> dict[str, object]:
    gym = get_gym_by_id(gym_id)
    if gym is None:
        raise HTTPException(status_code=404, detail="Gym not found")
    return serialize_gym(gym)


@app.post("/api/search")
def search_endpoint(request: SearchRequest) -> list[dict[str, object]]:
    filters = request.model_dump(exclude={"sort_key"}, exclude_none=True)
    try:
        return search_gym_records(filters, sort_key=request.sort_key)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/recommend")
def recommend_endpoint(request: RecommendationRequest) -> list[dict[str, object]]:
    return recommend_gym_records(request.model_dump(exclude_none=True))


@app.post("/api/compare")
def compare_endpoint(request: CompareRequest) -> list[dict[str, object]]:
    preferences = None
    if request.preferences is not None:
        preferences = request.preferences.model_dump(exclude_none=True)
    try:
        return compare_gym_records(request.gym_ids, preferences)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/gyms")
def create_gym(payload: GymPayload) -> dict[str, object]:
    gym_payload = payload.model_dump()
    gym_payload["gym_id"] = 0
    return create_gym_record(gym_payload)


@app.put("/api/gyms/{gym_id}")
def update_gym(gym_id: int, payload: GymPayload) -> dict[str, object]:
    updated = update_gym_record(gym_id, {"gym_id": gym_id, **payload.model_dump()})
    if updated is None:
        raise HTTPException(status_code=404, detail="Gym not found")
    return updated

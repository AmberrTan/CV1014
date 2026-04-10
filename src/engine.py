from geopy.distance import geodesic
from typing import List, Dict
import httpx
from .models import UserProfile, Gym, Recommendation, ScoreExplanation

async def fetch_real_gyms_from_osm(lat: float, lon: float, radius_km: float = 5.0) -> List[Gym]:
    """Fetch real gym data from OpenStreetMap using Overpass API"""
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Define the query: look for fitness_centre within a radius around lat, lon
    # 1km is approx 0.009 deg; we use around:radius in meters
    radius_m = radius_km * 1000
    query = f"""
    [out:json];
    node["leisure"="fitness_centre"](around:{radius_m},{lat},{lon});
    out body;
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(overpass_url, data=query, timeout=10.0)
            data = response.json()
            
            gyms = []
            for element in data.get("elements", []):
                tags = element.get("tags", {})
                gym_id = str(element.get("id"))
                name = tags.get("name", f"Gym {gym_id}")
                
                # Synthetic but grounded mapping (OSM doesn't have prices usually)
                # We'll assign random-ish but deterministic prices based on ID for demo
                price = 100.0 + (int(gym_id) % 150) 
                
                # Derive facilities from tags if possible, else defaults
                facilities = ["showers"]
                if tags.get("opening_hours") == "24/7": facilities.append("24h")
                if tags.get("female_friendly") == "yes": facilities.append("female-friendly")
                
                gyms.append(Gym(
                    gym_id=gym_id,
                    name=name,
                    location=(element["lat"], element["lon"]),
                    price=price,
                    facilities=facilities,
                    rating=4.0, # Default since OSM lacks ratings
                    popularity_score=0.5,
                    tags=list(tags.keys())
                ))
            return gyms
    except Exception as e:
        print(f"OSM Fetch Error: {e}")
        return []

def calculate_distance_score(distance_km: float, max_dist_km: float) -> float:
    """Closer = Higher Score [0, 1]"""
    if distance_km > max_dist_km:
        return 0.0
    if max_dist_km == 0:
        return 1.0
    return max(0.0, 1.0 - (distance_km / max_dist_km))

def calculate_budget_score(gym_price: float, budget_range: tuple) -> float:
    """Match between user budget and gym pricing [0, 1]"""
    min_b, max_b = budget_range
    if min_b <= gym_price <= max_b:
        return 1.0
    if gym_price < min_b:
        # User budget is higher than gym price, still a good match
        return 0.8
    if max_b == 0:
        return 0.0
    # Penalty for being over budget
    return max(0.0, 1.0 - (gym_price - max_b) / max_b)

def calculate_facility_score(user_prefs: Dict[str, bool], gym_facilities: List[str]) -> float:
    """Overlap between user preferences and gym features [0, 1]"""
    # Map preference keys to facility tags
    pref_map = {
        "access_24h": "24h",
        "requires_classes": "classes",
        "requires_shower_lockers": "showers",
        "female_friendly": "female-friendly"
    }
    
    requested = [pref_map[k] for k, v in user_prefs.items() if v and k in pref_map]
    if not requested:
        return 1.0
    
    matches = [f for f in requested if f in gym_facilities]
    return len(matches) / len(requested)

def calculate_rating_score(rating: float) -> float:
    """Normalize rating 0-5 to 0-1"""
    return rating / 5.0

def get_recommendations(user: UserProfile, gyms: List[Gym]) -> List[Recommendation]:
    recs = []
    
    # Weights from requirements
    W_DIST = 0.30
    W_BUDGET = 0.25
    W_FACILITY = 0.25
    W_RATING = 0.20
    
    user_prefs = {
        "access_24h": user.access_24h,
        "requires_classes": user.requires_classes,
        "requires_shower_lockers": user.requires_shower_lockers,
        "female_friendly": user.female_friendly
    }
    
    for gym in gyms:
        distance_km = geodesic(user.preferred_location, gym.location).km
        
        d_score = calculate_distance_score(distance_km, user.max_travel_distance_km)
        b_score = calculate_budget_score(gym.price, user.budget_range)
        f_score = calculate_facility_score(user_prefs, gym.facilities)
        r_score = calculate_rating_score(gym.rating)
        
        final_score = (
            W_DIST * d_score +
            W_BUDGET * b_score +
            W_FACILITY * f_score +
            W_RATING * r_score
        )
        
        recs.append(Recommendation(
            gym_id=gym.gym_id,
            name=gym.name,
            distance_km=round(distance_km, 2),
            score=round(final_score, 2),
            explanation=ScoreExplanation(
                distance=round(d_score, 2),
                budget=round(b_score, 2),
                facilities=round(f_score, 2),
                rating=round(r_score, 2)
            )
        ))
    
    # Sort by score descending
    recs.sort(key=lambda x: x.score, reverse=True)
    return recs

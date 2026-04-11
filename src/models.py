from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from enum import Enum

class FitnessGoal(str, Enum):
    muscle_gain = "muscle_gain"
    weight_loss = "weight_loss"
    general_fitness = "general_fitness"
    powerlifting = "powerlifting"
    cardio = "cardio"

class UserLocationProfile(BaseModel):
    user_id: str
    address_text: Optional[str] = None
    preferred_location: Tuple[float, float]

class UserProfile(BaseModel):
    user_id: str
    age_group: Optional[str] = None
    gender: Optional[str] = None
    budget_range: Tuple[float, float]
    preferred_location: Tuple[float, float] # (lat, lon)
    fitness_goals: List[FitnessGoal]
    access_24h: bool = False
    requires_classes: bool = False
    requires_shower_lockers: bool = False
    prefers_less_crowded: bool = False
    female_friendly: bool = False
    sport_filters: List[str] = []
    equipment_filters: List[str] = []
    max_travel_distance_km: float

class UserQuery(BaseModel):
    user_id: str
    access_24h: bool
    requires_classes: bool
    requires_shower_lockers: bool
    female_friendly: bool
    max_travel_distance_km: float
    budget_max: float

class Gym(BaseModel):
    gym_id: str
    name: str
    location: Tuple[float, float] # (lat, lon)
    price: float
    facilities: List[str]
    sports: List[str] = []
    equipment: List[str] = []
    rating: float
    popularity_score: float
    tags: List[str]

class ScoreExplanation(BaseModel):
    distance: float
    budget: float
    facilities: float
    rating: float

class Recommendation(BaseModel):
    gym_id: str
    name: str
    distance_km: float
    score: float
    explanation: ScoreExplanation

class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]
    pattern_insight: Optional[str] = None

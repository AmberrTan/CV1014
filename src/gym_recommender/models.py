from __future__ import annotations

from typing import TypedDict


class GoogleMapsLocation(TypedDict, total=False):
    latitude: float | None
    longitude: float | None


class GoogleMapsData(TypedDict, total=False):
    place_id: str | None
    display_name: str | None
    formatted_address: str | None
    location: GoogleMapsLocation
    google_maps_uri: str | None
    website_uri: str | None
    international_phone_number: str | None
    business_status: str | None
    primary_type: str | None
    types: list[str]
    rating: float | None
    user_rating_count: int | None
    open_now: bool | None
    weekday_descriptions: list[str]
    fetched_at: str


class OpenStreetMapData(TypedDict, total=False):
    osm_type: str | None
    osm_id: int | None
    place_id: int | None
    display_name: str | None
    name: str | None
    latitude: float | None
    longitude: float | None
    category: str | None
    type: str | None
    importance: float | None
    place_rank: int | None
    address: dict[str, str]
    namedetails: dict[str, str]
    extratags: dict[str, str]
    website: str | None
    opening_hours: str | None
    phone: str | None
    fetched_at: str


class GymRecordBase(TypedDict):
    gym_id: int
    gym_name: str
    area: str
    address: str
    x_coordinate: int
    y_coordinate: int
    monthly_price: float
    day_pass_price: float
    rating: float
    opening_time: int
    closing_time: int
    is_24_hours: bool
    gym_type: str
    facilities: list[str]
    beginner_friendly: bool
    female_friendly: bool
    student_discount: bool
    peak_crowd_level: str
    parking_available: bool
    near_mrt: bool
    trainer_available: bool
    classes_available: bool


class GymRecord(GymRecordBase, total=False):
    google_maps: GoogleMapsData
    openstreetmap: OpenStreetMapData


class SearchFilters(TypedDict, total=False):
    area: str
    max_budget: float
    min_rating: float
    required_facilities: list[str]
    open_at: int
    is_24_hours: bool
    classes_available: bool
    female_friendly: bool
    gym_type: str
    user_x: int
    user_y: int


class UserPreferences(TypedDict, total=False):
    preferred_area: str
    max_budget: float
    min_rating: float
    preferred_facilities: list[str]
    preferred_time: int
    female_friendly: bool
    classes_required: bool
    user_x: int
    user_y: int
    fitness_goal: str
    skill_level: str
    preferred_gym_type: str

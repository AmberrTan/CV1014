"""Typed dictionaries that describe the gym dataset schema."""

from __future__ import annotations

from typing import TypedDict


class OpenStreetMapData(TypedDict, total=False):
    """Enriched OpenStreetMap metadata for a gym."""

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
    """Fields required in the core gym dataset."""

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
    """Gym record with optional enrichment payloads."""

    openstreetmap: OpenStreetMapData


class SearchFilters(TypedDict, total=False):
    """User-provided filters for search and browse flows."""

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

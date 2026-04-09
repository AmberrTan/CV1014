"""Pydantic models for API payload validation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


def _is_valid_hhmm(value: int) -> bool:
    hours, minutes = divmod(value, 100)
    return (
        0 <= hours <= 24 and 0 <= minutes <= 59 and value != 2401 and (hours < 24 or minutes == 0)
    )


def _validate_time_value(value: int | None, field_name: str) -> int | None:
    if value is None:
        return None
    if not _is_valid_hhmm(value):
        raise ValueError(f"{field_name} must be a valid HHMM time")
    return value


def _validate_required_time(value: int, field_name: str) -> int:
    validated = _validate_time_value(value, field_name)
    if validated is None:
        raise ValueError(f"{field_name} must be provided")
    return validated


class PreferenceCoordinatesMixin(BaseModel):
    """Shared coordinate validation for search inputs."""

    user_x: int | None = None
    user_y: int | None = None

    @model_validator(mode="after")
    def validate_coordinates(self) -> "PreferenceCoordinatesMixin":
        has_user_x = self.user_x is not None
        has_user_y = self.user_y is not None
        if has_user_x != has_user_y:
            raise ValueError("user_x and user_y must be provided together")
        return self


class GymPayload(BaseModel):
    """Request payload for creating/updating a gym."""

    gym_name: str
    area: str
    address: str
    x_coordinate: int
    y_coordinate: int
    monthly_price: float
    day_pass_price: float
    rating: float = Field(ge=0, le=5)
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

    @field_validator("opening_time", "closing_time")
    @classmethod
    def validate_operating_time(cls, value: int, info) -> int:
        return _validate_required_time(value, info.field_name)

    @model_validator(mode="after")
    def validate_hours_window(self) -> "GymPayload":
        if not self.is_24_hours and self.opening_time >= self.closing_time:
            raise ValueError("non-24-hour gyms must have opening_time earlier than closing_time")
        return self


class SearchRequest(PreferenceCoordinatesMixin):
    """Request payload for search filters."""

    area: str | None = None
    max_budget: float | None = None
    min_rating: float | None = None
    required_facilities: list[str] = Field(default_factory=list)
    open_at: int | None = None
    is_24_hours: bool | None = None
    classes_available: bool | None = None
    female_friendly: bool | None = None
    gym_type: str | None = None
    sort_key: Literal["none", "price", "rating", "distance"] = "none"

    @field_validator("open_at")
    @classmethod
    def validate_open_at(cls, value: int | None) -> int | None:
        return _validate_time_value(value, "open_at")

    @model_validator(mode="after")
    def validate_distance_sort_requires_coordinates(self) -> "SearchRequest":
        if self.sort_key == "distance" and self.user_x is None:
            raise ValueError("distance sorting requires user_x and user_y")
        return self


class ComparePreferences(PreferenceCoordinatesMixin):
    """Optional scoring preferences for gym comparisons."""

    preferred_area: str | None = None
    max_budget: float | None = None
    min_rating: float | None = None
    preferred_facilities: list[str] = Field(default_factory=list)
    preferred_time: int | None = None
    female_friendly: bool | None = None
    classes_required: bool | None = None
    fitness_goal: str | None = None
    skill_level: str | None = None
    preferred_gym_type: str | None = None

    @field_validator("preferred_time")
    @classmethod
    def validate_preferred_time(cls, value: int | None) -> int | None:
        return _validate_time_value(value, "preferred_time")


class CompareRequest(BaseModel):
    """Request payload for comparing gyms."""

    gym_ids: list[int]
    preferences: ComparePreferences | None = None

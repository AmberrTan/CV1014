from src.engine import (
    build_overpass_query,
    is_valid_osm_name,
    extract_osm_facilities,
    get_element_location,
    gym_matches_hard_filters,
)
from src.models import UserProfile, Gym, FitnessGoal


def test_build_overpass_query_contains_expected_fragments():
    q = build_overpass_query(1.0, 2.0, 5000)
    assert "nwr" in q
    assert 'leisure"="fitness_centre"' in q
    assert 'amenity"="gym"' in q
    assert "out center" in q


def test_name_validation():
    assert is_valid_osm_name("Anytime Fitness")
    assert not is_valid_osm_name("Gym 12345")
    assert not is_valid_osm_name("")


def test_extract_osm_facilities():
    tags = {
        "opening_hours": "24/7",
        "female_friendly": "yes",
        "shower": "yes",
        "classes": "yes",
    }
    facilities = extract_osm_facilities(tags)
    assert "24h" in facilities
    assert "female-friendly" in facilities
    assert "showers" in facilities
    assert "classes" in facilities


def test_get_element_location_node_and_way():
    assert get_element_location({"lat": 1.1, "lon": 2.2}) == (1.1, 2.2)
    assert get_element_location({"center": {"lat": 3.3, "lon": 4.4}}) == (3.3, 4.4)
    assert get_element_location({}) is None


def test_gym_matches_hard_filters_strict_facilities():
    user = UserProfile(
        user_id="u1",
        budget_range=(0.0, 200.0),
        preferred_location=(1.0, 2.0),
        fitness_goals=[FitnessGoal.general_fitness],
        access_24h=True,
        requires_classes=True,
        requires_shower_lockers=True,
        female_friendly=True,
        sport_filters=["yoga"],
        equipment_filters=["treadmill"],
        max_travel_distance_km=5.0,
    )
    gym = Gym(
        gym_id="1",
        name="Gym A",
        location=(1.0, 2.0),
        price=100.0,
        facilities=["24h"],
        sports=[],
        equipment=[],
        rating=4.0,
        popularity_score=0.5,
        tags=[],
    )
    assert gym_matches_hard_filters(user, gym) is False

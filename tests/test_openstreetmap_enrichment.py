from __future__ import annotations

import unittest
from typing import cast

from gym_recommender.models import GymRecord, OpenStreetMapData
from gym_recommender.openstreetmap_enrichment import (
    build_openstreetmap_payload,
    build_osm_search_queries,
    build_osm_search_query,
    merge_openstreetmap_data,
)


class OpenStreetMapEnrichmentTests(unittest.TestCase):
    def test_build_osm_search_query_uses_existing_gym_fields(self) -> None:
        query = build_osm_search_query(
            {
                "gym_id": 1,
                "gym_name": "Anytime Fitness Jurong",
                "area": "Jurong East",
                "address": "Jurong Gateway Road",
                "x_coordinate": 12,
                "y_coordinate": 34,
                "monthly_price": 95.0,
                "day_pass_price": 20.0,
                "rating": 4.4,
                "opening_time": 0,
                "closing_time": 2400,
                "is_24_hours": True,
                "gym_type": "commercial",
                "facilities": ["cardio"],
                "beginner_friendly": True,
                "female_friendly": True,
                "student_discount": False,
                "peak_crowd_level": "high",
                "parking_available": True,
                "near_mrt": True,
                "trainer_available": True,
                "classes_available": True,
            }
        )
        self.assertEqual(
            query,
            "Anytime Fitness Jurong, Jurong Gateway Road, Jurong East, Singapore",
        )

    def test_build_openstreetmap_payload_extracts_core_fields(self) -> None:
        payload = build_openstreetmap_payload(
            {
                "osm_type": "way",
                "osm_id": 12345,
                "place_id": 67890,
                "display_name": "Gym, Jurong East, Singapore",
                "name": "Gym",
                "lat": "1.333",
                "lon": "103.742",
                "category": "leisure",
                "type": "fitness_centre",
                "importance": 0.52,
                "place_rank": 30,
                "address": {"suburb": "Jurong East"},
                "namedetails": {"name": "Gym"},
                "extratags": {
                    "website": "https://example.com",
                    "opening_hours": "24/7",
                    "contact:phone": "+65 1234 5678",
                },
            }
        )

        self.assertEqual(payload["osm_type"], "way")
        self.assertEqual(payload["osm_id"], 12345)
        self.assertEqual(payload["latitude"], 1.333)
        self.assertEqual(payload["longitude"], 103.742)
        self.assertEqual(payload["website"], "https://example.com")
        self.assertEqual(payload["opening_hours"], "24/7")
        self.assertEqual(payload["phone"], "+65 1234 5678")

    def test_build_osm_search_queries_creates_fallback_variants(self) -> None:
        queries = build_osm_search_queries(
            {
                "gym_id": 1,
                "gym_name": "Anytime Fitness Jurong",
                "area": "Jurong East",
                "address": "Jurong Gateway Road",
                "x_coordinate": 12,
                "y_coordinate": 34,
                "monthly_price": 95.0,
                "day_pass_price": 20.0,
                "rating": 4.4,
                "opening_time": 0,
                "closing_time": 2400,
                "is_24_hours": True,
                "gym_type": "commercial",
                "facilities": ["cardio"],
                "beginner_friendly": True,
                "female_friendly": True,
                "student_discount": False,
                "peak_crowd_level": "high",
                "parking_available": True,
                "near_mrt": True,
                "trainer_available": True,
                "classes_available": True,
            }
        )

        self.assertEqual(
            queries,
            [
                "Anytime Fitness Jurong, Jurong Gateway Road, Jurong East, Singapore",
                "Anytime Fitness Jurong, Jurong East, Singapore",
                "Anytime Fitness Jurong, Singapore",
                "Anytime Fitness Jurong",
            ],
        )

    def test_merge_openstreetmap_data_adds_nested_payload(self) -> None:
        gym = {
            "gym_id": 1,
            "gym_name": "Anytime Fitness Jurong",
            "area": "Jurong East",
            "address": "Jurong Gateway Road",
            "x_coordinate": 12,
            "y_coordinate": 34,
            "monthly_price": 95.0,
            "day_pass_price": 20.0,
            "rating": 4.4,
            "opening_time": 0,
            "closing_time": 2400,
            "is_24_hours": True,
            "gym_type": "commercial",
            "facilities": ["cardio"],
            "beginner_friendly": True,
            "female_friendly": True,
            "student_discount": False,
            "peak_crowd_level": "high",
            "parking_available": True,
            "near_mrt": True,
            "trainer_available": True,
            "classes_available": True,
        }

        merged = merge_openstreetmap_data(
            cast(GymRecord, gym),
            cast(OpenStreetMapData, {"osm_id": 12345}),
        )

        self.assertEqual(merged["openstreetmap"]["osm_id"], 12345)
        self.assertEqual(merged["gym_name"], gym["gym_name"])


if __name__ == "__main__":
    unittest.main()

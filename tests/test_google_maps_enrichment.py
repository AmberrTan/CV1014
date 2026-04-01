from __future__ import annotations

import unittest
from typing import cast

from gym_recommender.google_maps_enrichment import (
    build_google_maps_payload,
    build_text_search_query,
    merge_google_maps_data,
)
from gym_recommender.models import GoogleMapsData, GymRecord


class GoogleMapsEnrichmentTests(unittest.TestCase):
    def test_build_text_search_query_uses_existing_gym_fields(self) -> None:
        query = build_text_search_query(
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

    def test_build_google_maps_payload_prefers_place_details_fields(self) -> None:
        payload = build_google_maps_payload(
            {
                "id": "from-search",
                "displayName": {"text": "Search Name"},
                "formattedAddress": "Search Address",
                "location": {"latitude": 1.1, "longitude": 2.2},
                "types": ["gym"],
                "googleMapsUri": "https://maps.google.com/search",
                "businessStatus": "OPERATIONAL",
                "primaryType": "gym",
            },
            {
                "id": "from-details",
                "displayName": {"text": "Detail Name"},
                "formattedAddress": "Detail Address",
                "location": {"latitude": 3.3, "longitude": 4.4},
                "googleMapsUri": "https://maps.google.com/details",
                "websiteUri": "https://example.com",
                "internationalPhoneNumber": "+65 1234 5678",
                "regularOpeningHours": {
                    "openNow": True,
                    "weekdayDescriptions": ["Monday: Open 24 hours"],
                },
                "rating": 4.7,
                "userRatingCount": 128,
                "businessStatus": "OPERATIONAL",
                "primaryType": "fitness_center",
                "types": ["gym", "point_of_interest"],
            },
        )

        self.assertEqual(payload["place_id"], "from-details")
        self.assertEqual(payload["display_name"], "Detail Name")
        self.assertEqual(payload["formatted_address"], "Detail Address")
        self.assertEqual(payload["location"]["latitude"], 3.3)
        self.assertEqual(payload["website_uri"], "https://example.com")
        self.assertTrue(payload["open_now"])
        self.assertEqual(payload["types"], ["gym", "point_of_interest"])

    def test_merge_google_maps_data_adds_nested_payload(self) -> None:
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

        merged = merge_google_maps_data(
            cast(GymRecord, gym),
            cast(GoogleMapsData, {"place_id": "abc123"}),
        )

        self.assertEqual(merged["google_maps"]["place_id"], "abc123")
        self.assertEqual(merged["gym_name"], gym["gym_name"])


if __name__ == "__main__":
    unittest.main()

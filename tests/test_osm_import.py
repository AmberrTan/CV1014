from __future__ import annotations

import unittest

from gym_recommender.osm_import import _normalize_element, coordinate_to_grid


class OsmImportTests(unittest.TestCase):
    def test_coordinate_to_grid_scales_into_expected_range(self) -> None:
        x_value, y_value = coordinate_to_grid(1.35, 103.82)
        self.assertGreaterEqual(x_value, 0)
        self.assertLessEqual(x_value, 100)
        self.assertGreaterEqual(y_value, 0)
        self.assertLessEqual(y_value, 100)

    def test_normalize_element_builds_app_record(self) -> None:
        gym = _normalize_element(
            {
                "type": "node",
                "id": 123,
                "lat": 1.35,
                "lon": 103.82,
                "tags": {
                    "name": "UFIT CBD Hub",
                    "addr:housenumber": "21",
                    "addr:street": "Club Street",
                    "addr:city": "Singapore",
                    "addr:postcode": "069410",
                    "leisure": "fitness_centre",
                    "website": "https://ufit.com.sg/",
                    "phone": "+65 62255059",
                },
            },
            gym_id=1,
        )

        assert gym is not None
        self.assertEqual(gym["gym_name"], "UFIT CBD Hub")
        self.assertEqual(gym["gym_type"], "group training")
        self.assertIn("personal training", gym["facilities"])
        self.assertIn("openstreetmap", gym)
        self.assertEqual(gym["area"], "Singapore")

    def test_normalize_element_uses_address_missing_fallback(self) -> None:
        gym = _normalize_element(
            {
                "type": "node",
                "id": 124,
                "lat": 1.35,
                "lon": 103.82,
                "tags": {
                    "name": "No Address Gym",
                    "leisure": "fitness_centre",
                },
            },
            gym_id=1,
        )

        assert gym is not None
        self.assertEqual(gym["address"], "Address missing")


if __name__ == "__main__":
    unittest.main()

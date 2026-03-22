from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gym_recommender.data import generate_next_gym_id, load_database, save_database
from gym_recommender.recommendation import calculate_match_score, recommend_gyms
from gym_recommender.services import compare_gym_records, search_gym_records
from gym_recommender.search import calculate_distance, search_gyms, sort_gyms

try:
    from fastapi.testclient import TestClient
    from gym_recommender.api import app
except Exception:  # pragma: no cover - optional in sandbox without dependency install
    TestClient = None
    app = None


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "data" / "gyms.json"


class GymSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gyms = load_database(FIXTURE_PATH)

    def test_load_save_round_trip_preserves_facilities(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "gyms.json"
            save_database(self.gyms, temp_path)
            reloaded = load_database(temp_path)

        self.assertEqual(len(reloaded), len(self.gyms))
        self.assertEqual(reloaded[0]["facilities"], self.gyms[0]["facilities"])

    def test_generate_next_gym_id(self) -> None:
        self.assertEqual(generate_next_gym_id(self.gyms), 13)

    def test_search_filters_by_area_budget_rating_and_facility(self) -> None:
        results = search_gyms(
            self.gyms,
            {
                "area": "Jurong East",
                "max_budget": 100.0,
                "min_rating": 4.0,
                "required_facilities": ["shower"],
            },
        )
        self.assertEqual([gym["gym_id"] for gym in results], [1])

    def test_search_filters_by_open_time(self) -> None:
        results = search_gyms(self.gyms, {"open_at": 2330})
        self.assertTrue(all(gym["is_24_hours"] for gym in results))

    def test_sort_by_price(self) -> None:
        sorted_gyms = sort_gyms(self.gyms[:5], "price")
        self.assertEqual(sorted_gyms[0]["gym_id"], 3)

    def test_sort_by_rating(self) -> None:
        sorted_gyms = sort_gyms(self.gyms[:5], "rating")
        self.assertEqual(sorted_gyms[0]["gym_id"], 5)

    def test_sort_by_distance(self) -> None:
        sorted_gyms = sort_gyms(self.gyms[:3], "distance", user_x=10, user_y=30)
        self.assertEqual(sorted_gyms[0]["gym_id"], 1)

    def test_distance_calculation(self) -> None:
        self.assertAlmostEqual(calculate_distance(0, 0, 3, 4), 5.0)

    def test_recommendation_returns_ranked_results(self) -> None:
        recommendations = recommend_gyms(
            self.gyms,
            {
                "preferred_area": "Raffles Place",
                "max_budget": 250.0,
                "min_rating": 4.0,
                "preferred_facilities": ["group classes"],
                "classes_required": True,
                "user_x": 60,
                "user_y": 70,
                "fitness_goal": "general fitness",
                "skill_level": "beginner",
            },
        )
        self.assertGreaterEqual(len(recommendations), 1)
        self.assertGreaterEqual(recommendations[0][1], recommendations[-1][1])

    def test_match_score_stays_in_percentage_range(self) -> None:
        score = calculate_match_score(
            self.gyms[0],
            {
                "max_budget": 120.0,
                "preferred_facilities": ["cardio", "shower"],
                "fitness_goal": "general fitness",
                "skill_level": "beginner",
                "user_x": 20,
                "user_y": 20,
            },
        )
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)

    def test_service_search_returns_serialized_distance(self) -> None:
        results = search_gym_records(
            {
                "area": "Jurong East",
                "user_x": 10,
                "user_y": 30,
            },
            sort_key="distance",
        )
        self.assertEqual(results[0]["gym_id"], 1)
        self.assertIn("distance", results[0])

    def test_service_search_distance_without_coordinates_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "distance sorting requires user_x and user_y"):
            search_gym_records({}, sort_key="distance")

    def test_compare_records_returns_selected_gyms_in_request_order(self) -> None:
        comparison = compare_gym_records([3, 1, 5])
        self.assertEqual([gym["gym_id"] for gym in comparison], [3, 1, 5])

    def test_compare_records_rejects_duplicate_gym_ids(self) -> None:
        with self.assertRaisesRegex(ValueError, "distinct gym IDs"):
            compare_gym_records([1, 3, 1])

    def test_compare_records_rejects_unknown_gym_ids(self) -> None:
        with self.assertRaisesRegex(ValueError, "not found"):
            compare_gym_records([1, 999])

    @unittest.skipIf(TestClient is None, "fastapi not installed in this environment")
    def test_api_get_gyms(self) -> None:
        client = TestClient(app)
        response = client.get("/api/gyms")

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 1)

    @unittest.skipIf(TestClient is None, "fastapi not installed in this environment")
    def test_api_recommend(self) -> None:
        client = TestClient(app)
        response = client.post(
            "/api/recommend",
            json={
                "preferred_area": "Raffles Place",
                "max_budget": 250.0,
                "preferred_facilities": ["group classes"],
                "classes_required": True,
                "fitness_goal": "general fitness",
                "skill_level": "beginner",
                "user_x": 60,
                "user_y": 70,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 1)

    @unittest.skipIf(TestClient is None, "fastapi not installed in this environment")
    def test_api_compare_rejects_duplicate_gym_ids(self) -> None:
        client = TestClient(app)
        response = client.post("/api/compare", json={"gym_ids": [1, 1]})

        self.assertEqual(response.status_code, 400)
        self.assertIn("distinct gym IDs", response.json()["detail"])

    @unittest.skipIf(TestClient is None, "fastapi not installed in this environment")
    def test_api_compare_rejects_unknown_gym_ids(self) -> None:
        client = TestClient(app)
        response = client.post("/api/compare", json={"gym_ids": [1, 999]})

        self.assertEqual(response.status_code, 400)
        self.assertIn("not found", response.json()["detail"])

    @unittest.skipIf(TestClient is None, "fastapi not installed in this environment")
    def test_api_compare_returns_gyms_in_request_order(self) -> None:
        client = TestClient(app)
        response = client.post("/api/compare", json={"gym_ids": [3, 1]})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([gym["gym_id"] for gym in response.json()], [3, 1])

    @unittest.skipIf(TestClient is None, "fastapi not installed in this environment")
    def test_api_search_rejects_invalid_sort_key(self) -> None:
        client = TestClient(app)
        response = client.post("/api/search", json={"sort_key": "nearest"})

        self.assertEqual(response.status_code, 422)

    @unittest.skipIf(TestClient is None, "fastapi not installed in this environment")
    def test_api_search_rejects_distance_sort_without_coordinates(self) -> None:
        client = TestClient(app)
        response = client.post("/api/search", json={"sort_key": "distance"})

        self.assertEqual(response.status_code, 422)

    @unittest.skipIf(TestClient is None, "fastapi not installed in this environment")
    def test_api_search_distance_sort_returns_distance(self) -> None:
        client = TestClient(app)
        response = client.post(
            "/api/search",
            json={"sort_key": "distance", "user_x": 10, "user_y": 30},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload[0]["gym_id"], 1)
        self.assertIn("distance", payload[0])

    @unittest.skipIf(TestClient is None, "fastapi not installed in this environment")
    def test_api_search_rejects_invalid_open_time(self) -> None:
        client = TestClient(app)
        response = client.post("/api/search", json={"open_at": 2500})

        self.assertEqual(response.status_code, 422)

    @unittest.skipIf(TestClient is None, "fastapi not installed in this environment")
    def test_api_recommend_rejects_invalid_preferred_time(self) -> None:
        client = TestClient(app)
        response = client.post("/api/recommend", json={"preferred_time": 2360})

        self.assertEqual(response.status_code, 422)

    @unittest.skipIf(TestClient is None, "fastapi not installed in this environment")
    def test_api_create_gym_rejects_invalid_non_24_hour_schedule(self) -> None:
        client = TestClient(app)
        response = client.post(
            "/api/gyms",
            json={
                "gym_name": "Invalid Hours Gym",
                "area": "Test",
                "address": "1 Test Road",
                "x_coordinate": 1,
                "y_coordinate": 2,
                "monthly_price": 99.0,
                "day_pass_price": 10.0,
                "rating": 4.0,
                "opening_time": 2200,
                "closing_time": 600,
                "is_24_hours": False,
                "gym_type": "commercial",
                "facilities": ["cardio"],
                "beginner_friendly": True,
                "female_friendly": True,
                "student_discount": False,
                "peak_crowd_level": "medium",
                "parking_available": False,
                "near_mrt": True,
                "trainer_available": False,
                "classes_available": False,
            },
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()

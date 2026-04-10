from .models import Gym

MOCK_GYMS = [
    Gym(
        gym_id="sg_001",
        name="Tanjong Pagar Iron Works",
        location=(1.2765, 103.8447), # Tanjong Pagar
        price=180.0,
        facilities=["24h", "classes", "showers", "powerlifting"],
        rating=4.7,
        popularity_score=0.95,
        tags=["powerlifting", "cbd", "24/7"]
    ),
    Gym(
        gym_id="sg_002",
        name="Orchard Wellness Elite",
        location=(1.3048, 103.8318), # Orchard Road
        price=250.0,
        facilities=["classes", "showers", "pool", "spa", "female-friendly"],
        rating=4.9,
        popularity_score=0.85,
        tags=["luxury", "wellness", "central"]
    ),
    Gym(
        gym_id="sg_003",
        name="HDB Heartland Fitness",
        location=(1.3329, 103.7436), # Jurong East
        price=80.0,
        facilities=["24h", "showers"],
        rating=3.8,
        popularity_score=0.9,
        tags=["affordable", "heartland"]
    ),
    Gym(
        gym_id="sg_004",
        name="Novena Active Studio",
        location=(1.3204, 103.8435), # Novena
        price=150.0,
        facilities=["classes", "showers", "female-friendly"],
        rating=4.4,
        popularity_score=0.7,
        tags=["boutique", "classes"]
    ),
    Gym(
        gym_id="sg_005",
        name="Paya Lebar Power Hub",
        location=(1.3182, 103.8928), # Paya Lebar
        price=120.0,
        facilities=["24h", "classes", "showers"],
        rating=4.2,
        popularity_score=0.8,
        tags=["24/7", "convenient"]
    )
]

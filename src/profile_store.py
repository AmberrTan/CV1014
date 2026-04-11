from typing import Dict, Optional

from .models import UserLocationProfile

_PROFILE_STORE: Dict[str, UserLocationProfile] = {}


def save_profile(profile: UserLocationProfile) -> None:
    _PROFILE_STORE[profile.user_id] = profile


def get_profile(user_id: str) -> Optional[UserLocationProfile]:
    return _PROFILE_STORE.get(user_id)

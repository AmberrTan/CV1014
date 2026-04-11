from typing import List


def split_normalized(value: str) -> List[str]:
    if not value:
        return []
    parts: List[str] = []
    for chunk in value.replace(",", ";").split(";"):
        cleaned = chunk.strip().lower()
        if cleaned:
            parts.append(cleaned)
    return parts

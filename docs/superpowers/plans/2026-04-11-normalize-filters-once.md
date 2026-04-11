# Normalize Filters Once Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Precompute normalized sport/equipment filters once per OSM query and thread them through helpers to avoid repeated normalization.

**Architecture:** Add a small helper to compute normalized filter lists, then update query-building helpers to accept these lists and stop re-normalizing. External behavior remains unchanged.

**Tech Stack:** Python, FastAPI, Pydantic

---

## File Structure
- Modify: `/Users/zhoufuwang/Projects/cv1014_2/.worktrees/unused-code-cleanup/src/engine.py`

### Task 1: Thread Normalized Filters Through OSM Helpers

**Files:**
- Modify: `/Users/zhoufuwang/Projects/cv1014_2/.worktrees/unused-code-cleanup/src/engine.py`

- [ ] **Step 1: Add a helper to compute normalized filters**

```python
def _get_normalized_filters(user: Optional[UserProfile]) -> Tuple[List[str], List[str]]:
    if not user:
        return [], []
    return (
        normalize_user_filters(user.sport_filters),
        normalize_user_filters(user.equipment_filters),
    )
```

- [ ] **Step 2: Update filter helpers to accept precomputed lists**

```python
def _build_filter_suffixes(
    user: UserProfile,
    *,
    sport_filters: Optional[List[str]] = None,
    equipment_filters: Optional[List[str]] = None,
) -> List[str]:
    suffixes: List[str] = []

    if user.access_24h:
        suffixes.append('["opening_hours"="24/7"]')

    if user.requires_classes:
        suffixes.extend([
            f'["classes"~"{TRUTHY_REGEX}"]',
            f'["fitness_classes"~"{TRUTHY_REGEX}"]',
            f'["group_classes"~"{TRUTHY_REGEX}"]',
        ])

    if user.female_friendly:
        suffixes.append(f'["female_friendly"~"{TRUTHY_REGEX}"]')

    sport_values = _escape_regex_values(sport_filters or normalize_user_filters(user.sport_filters))
    if sport_values:
        suffixes.append(f'["sport"~"{sport_values}"]')

    equipment_values = _escape_regex_values(equipment_filters or normalize_user_filters(user.equipment_filters))
    if equipment_values:
        suffixes.append(f'["equipment"~"{equipment_values}"]')

    return suffixes or [""]


def _sport_regex_with_user(
    user: Optional[UserProfile],
    base_regex: str,
    *,
    sport_filters: Optional[List[str]] = None,
) -> str:
    if not user:
        return base_regex
    extra = _escape_regex_values(sport_filters or normalize_user_filters(user.sport_filters))
    if extra:
        return f"{base_regex}|{extra}"
    return base_regex
```

- [ ] **Step 3: Update query builders to compute once and pass through**

```python
def build_overpass_query(
    lat: float,
    lon: float,
    radius_m: int,
    user: Optional[UserProfile] = None,
) -> str:
    sport_filters, equipment_filters = _get_normalized_filters(user)
    suffixes = _build_filter_suffixes(
        user,
        sport_filters=sport_filters,
        equipment_filters=equipment_filters,
    ) if user else [""]
    selectors = [
        'nwr["leisure"="fitness_centre"]',
        'nwr["leisure"="fitness_station"]',
        f'nwr["leisure"="sports_centre"]["sport"~"{_sport_regex_with_user(user, "fitness|weightlifting|crossfit|gym", sport_filters=sport_filters)}"]',
        'nwr["amenity"="gym"]',
    ]
    location_clause = f"(around:{radius_m},{lat},{lon});"
    parts = _build_selector_parts(selectors, suffixes, location_clause, user=user)
    return "[out:json][timeout:120];(" + parts + ");out center tags;"


def build_overpass_country_query(
    country_code: str = "SG",
    user: Optional[UserProfile] = None,
) -> str:
    sport_filters, equipment_filters = _get_normalized_filters(user)
    suffixes = _build_filter_suffixes(
        user,
        sport_filters=sport_filters,
        equipment_filters=equipment_filters,
    ) if user else [""]
    selectors = [
        'nwr["amenity"="gym"]',
        'nwr["leisure"="fitness_centre"]',
    ]
    location_clause = "(area.searchArea);"
    parts = _build_selector_parts(selectors, suffixes, location_clause)
    return (
        "[out:json][timeout:120];"
        f'area["ISO3166-1"="{country_code}"][admin_level=2]->.searchArea;'
        "(" + parts + ");out center tags;"
    )
```

- [ ] **Step 4: Sanity scan for lingering repeated normalization**

Run:
```bash
rg -n "normalize_user_filters\(user\.sport_filters\)|normalize_user_filters\(user\.equipment_filters\)" /Users/zhoufuwang/Projects/cv1014_2/.worktrees/unused-code-cleanup/src/engine.py
```
Expected: only in `_get_normalized_filters` and any non-OSM scoring helpers that legitimately use it.

- [ ] **Step 5: Commit**

```bash
git add /Users/zhoufuwang/Projects/cv1014_2/.worktrees/unused-code-cleanup/src/engine.py

git commit -m "Normalize OSM filters once"
```


# Normalize Filters Once Design

## Goal
Reduce repeated normalization of user filters by computing normalized sport/equipment filters once per OSM query and threading them through helper functions.

## Scope
- Add a small helper to compute normalized filter lists.
- Update internal query-building helpers to accept precomputed normalized lists.
- Keep external behavior the same.

## Non-Goals
- No functional changes to recommendations or API responses.
- No refactor of unrelated logic.

## Approach
1. Add a helper in `src/engine.py` that returns normalized sport/equipment filters for a `UserProfile`.
2. Update `_build_filter_suffixes` and `_sport_regex_with_user` to accept normalized lists (optional) to avoid re-normalizing.
3. Update `build_overpass_query` and `build_overpass_country_query` to pass the normalized lists into those helpers.

## Impact
- Slightly fewer lines of repeated normalization.
- Centralized normalization logic for OSM query filters.

## Testing
- No tests required; behavior should remain unchanged.

## Rollback
- Revert the commit if any query behavior changes are observed.

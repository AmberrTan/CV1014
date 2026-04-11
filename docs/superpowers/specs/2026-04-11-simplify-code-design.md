# Simplify Codebase (Fewer Lines + Less Duplication)

## Context
We will refactor the existing CV1014 codebase to reduce line count and duplication, while keeping behavior stable except for small improvements in input parsing and error clarity (explicitly approved by the user).

## Goals
- Reduce code duplication and overall lines without large structural churn.
- Improve input parsing forgiveness (extra spaces, comma variants, empty inputs).
- Improve clarity of user-facing error messages.
- Keep output and behavior otherwise consistent.

## Non-Goals
- Large architectural changes or file splits (no module re-organization).
- Changing core search/filter semantics.
- UI redesign or visual changes.

## Proposed Changes

### 1) TUI Parsing and Status Handling (`src/gym_recommender/tui.py`)
- Add small helper(s) for:
  - Parsing optional numbers with consistent behavior and messages.
  - Standardizing status updates that also clear result lists/tables.
- Update search input parsing to accept whitespace and comma variants.
- Improve error messages for missing/partial input, e.g. coordinates.

### 2) Gym List Item Creation (`src/gym_recommender/tui.py`)
- Add a single helper to create a `ListItem` for a gym and attach `GymListItem` data.
- Use it in both browse and search flows.

### 3) Compare Flow Consolidation (`src/gym_recommender/tui.py`)
- Consolidate ID parsing and validation in one place.
- Remove duplicate validation in `_run_compare()` and rely on a single source of truth.
- Improve messages for invalid IDs (empty, non-numeric, too many/few, duplicates).

### 4) Inference Helper De-duplication (`scripts/fetch_gyms.py`)
- Add `_has_any(haystack: str, keywords: Iterable[str]) -> bool`.
- Introduce `AREA_KEYS` for shared area lookup logic.
- Replace repeated keyword checks with `_has_any` and unify area selection in `_build_area()` and `reverse_geocode_area()`.

### 5) Search Utilities (`src/gym_recommender/search.py`)
- Make minimal simplifications only if they reduce duplication without obscuring logic.

## Data Flow and Error Handling
- No changes to stored data format or API usage.
- Error messages in TUI are clarified and more specific, but no new error classes are introduced.

## Testing
- Run existing tests (`pytest`).
- Ensure the existing TUI still launches and screens load (manual smoke check if needed).

## Risks and Mitigations
- Risk: subtle behavior change due to refactors in parsing logic.
  - Mitigation: keep parsing helpers strict on numeric conversion but more tolerant of whitespace; keep filter semantics unchanged.
- Risk: refactors in OSM inference introduce discrepancies.
  - Mitigation: strictly refactor to reuse shared helpers without changing keywords or thresholds.

## Rollout Plan
1. Implement refactors in `tui.py` and `search.py`.
2. Implement helper refactors in `fetch_gyms.py`.
3. Run tests; adjust if needed.
4. Provide a simplification report comparing before/after.

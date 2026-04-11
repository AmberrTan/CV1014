# OSM Gym Fetch Refinement — Design

Date: 2026-04-11

## Summary
Refine OSM fetching so it returns more real gyms with fewer noisy placeholders, and ensure user-selected filters from the UI are applied strictly using OSM tags. Expand the Overpass query to include broader gym-related tags across nodes/ways/relations, post-filter for name quality, and dedupe overlapping OSM objects. Keep deterministic synthetic pricing for budget scoring.

## Goals
- Fetch more real gyms (OSM nodes/ways/relations) around the user’s location.
- Apply strict filter logic based on UI filters (24h, showers, classes, female-friendly, sports, equipment).
- Exclude noisy placeholder results (e.g., “Gym 11754949223”).
- Maintain current budget scoring with deterministic synthetic pricing.
- Preserve fallback to mock/synthetic gyms when OSM yields too few valid results.

## Non-goals
- Adding new user-facing filters or changing UI fields.
- Introducing external data sources beyond OSM Overpass.
- Changing recommendation scoring weights.

## Proposed Approach
### Overpass Query Expansion
- Use `nwr` instead of `node` to include nodes, ways, and relations.
- Query tags:
  - `leisure=fitness_centre`
  - `leisure=fitness_station`
  - `leisure=sports_centre` + `sport` in `fitness|weightlifting|crossfit|gym`
  - `amenity=gym`
- Use `out center;` to extract coordinates for ways/relations.
- Prefer `name` tag; drop results without a valid name in post-filtering.

### Tag Extraction & Strict Filter Matching
- Map OSM tags to internal facilities:
  - `opening_hours=24/7` → `24h`
  - `female_friendly=yes` → `female-friendly`
  - `shower=yes` or `toilets:shower=yes` → `showers`
  - `classes=yes`, `fitness_classes=yes`, `group_classes=yes` → `classes`
- Sports/equipment derived from `sport`, `equipment`, `gym`, `fitness_station` tags using the existing normalized split logic.
- Strict filtering: if a user filter is set and the gym lacks an explicit tag match, exclude it.
- Keep deterministic synthetic price based on OSM id to preserve budget scoring.

### Result Cleanup
- Drop OSM results if `name` is missing or matches `^gym\s*\d+$` (case-insensitive).
- Dedupe gyms with the same name and near-identical location (e.g., within 50–100m) to reduce node/way duplicates.
- Keep existing fallback to `ensure_minimum_gyms` if valid OSM gyms are too few.

## Data Flow
1. Build Overpass query from user location and radius.
2. Fetch raw OSM elements.
3. Normalize tags, extract facilities/sports/equipment.
4. Filter out unnamed and placeholder names.
5. Apply strict user filters.
6. Dedupe results.
7. Return gyms; if too few, pad with mock/synthetic gyms.

## Error Handling
- If Overpass fails or returns invalid JSON, log error and return empty list to allow fallback.
- Continue to treat OSM as best-effort; no user-facing error changes.

## Testing Notes
- Add unit-like checks or manual validation to ensure:
  - Broader query returns more gyms than node-only query.
  - Filters exclude gyms missing tags when filters are set.
  - Placeholder names like “Gym 123” are removed.
  - Deduplication removes node/way duplicates by name+location.

## Open Questions
None (decisions confirmed).

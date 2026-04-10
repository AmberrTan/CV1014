# TUI Area Partial Match (Substring) Design

## Summary
Improve the Textual TUI search experience by allowing case-insensitive substring matching on the `area` input. If the input matches exactly one area, use it and run search. If multiple areas match, show all matches and do not run. If none match, show a friendly message with valid areas. This avoids false “no results” for partial entries like `Jurong`.

## Goals
- Accept partial area inputs (substring match) in the TUI search screen.
- Provide clear feedback when input is ambiguous or invalid.
- Keep behavior consistent with existing search filters and UI patterns.

## Non-Goals
- No regex parsing or full regular expression support.
- No changes to the dataset, search algorithm, or backend services.
- No UI layout changes beyond status messaging.

## User Flow
1. User types an area substring (e.g., `Jurong`) and presses Enter or clicks Search.
2. The app attempts to resolve the area:
   - **One match**: use that area and run the search.
   - **Multiple matches**: show all matches in status; do not run.
   - **No matches**: show a message with valid areas; do not run.
3. If search runs, results list updates and status shows match + count.

## Behavior Details
- Matching is **case-insensitive** substring match against the known area list derived from dataset.
- Exact match counts as a single match.
- When multiple matches are found, the search is not executed and results list is cleared.
- When no matches are found, the search is not executed and results list is cleared.
- Status message concatenates any resolution note with the results count when search succeeds.

## Implementation Notes
- Add a helper in `SearchScreen` to resolve the `area` input to a single dataset area or return a status message when ambiguous or invalid.
- Use the existing `GymTuiApp.get_areas()` to access canonical area values.
- Keep other filters unchanged.

## Error Handling
- Ambiguous area: `Area 'X' matches multiple areas: A, B, C.`
- No match: `Area 'X' not found. Try: ...`
- Successful resolution: `Using area 'A' for 'X'. Found N gyms.`

## Testing
- Manual smoke test:
  - Input `Jurong` → resolves to `Jurong East`, returns results.
  - Input `a` → shows multiple matches, no results list update.
  - Input unknown string → shows valid areas, no results.

## Rollout
- Update TUI module only; no migrations or API changes.


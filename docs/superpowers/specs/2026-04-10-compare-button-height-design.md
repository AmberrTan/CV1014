# Compare Button Height Alignment (Design)

Date: 2026-04-10

## Goal
Make the Compare button exactly the same height as the Gym IDs input (including borders) across all breakpoints.

## Scope
In scope:
- Compare page toolbar only.
- CSS override to align button and input heights.

Out of scope:
- Global button or input styles.
- Other pages.

## Proposed Approach
- Add a compare-specific class on the compare toolbar (e.g., `toolbar--compare`).
- Define a shared CSS custom property for field height in that scope.
- Apply the same height to the input and Compare button so the boxes align exactly.

## UI Details
- Use a single height token (e.g., `--compare-field-height`) on the compare toolbar.
- Set `height` for the input and the compare button to the same value.
- Keep existing padding/font sizes unless needed for perfect height match.

## Acceptance Criteria
- Compare button and input are the same height including border.
- Alignment holds at all responsive breakpoints.
- No changes to other pages.

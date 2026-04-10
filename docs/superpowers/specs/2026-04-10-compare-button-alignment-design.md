# Compare Button Alignment (Design)

Date: 2026-04-10

## Goal
Make the Compare button on the compare page smaller and aligned to the input field baseline to better match the page layout.

## Scope
In scope:
- Update compare page toolbar alignment to baseline.
- Use a compact button style for the Compare button.

Out of scope:
- Other pages or global button styles.
- Layout changes outside the compare page toolbar.

## Proposed Approach
- Adjust the compare page toolbar container to align items on the baseline.
- Apply a compact button style (reduced padding and font size) to the Compare button only.
- Keep the input field layout unchanged.

## UI Details
- Toolbar alignment: `align-items: baseline` (or equivalent) so the button sits on the same baseline as the input.
- Button size: smaller padding and font size to visually match the input height.
- No change to button label or behavior.

## Acceptance Criteria
- Compare button is visibly smaller than the default button.
- Compare button baseline aligns with the input field in the toolbar.
- No regressions to other pages.

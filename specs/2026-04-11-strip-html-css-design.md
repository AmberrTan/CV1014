# Strip HTML CSS Design

## Goal
Remove all CSS from the static HTML pages so they render using browser defaults.

## Scope
- `src/static/index.html`
- `src/static/profile.html`

## Non-Goals
- No layout or content changes beyond removing CSS.
- No JavaScript changes.

## Approach
1. Remove all `<style>...</style>` blocks.
2. Remove all `<link rel="stylesheet" ...>` tags.
3. Remove all inline `style="..."` attributes.

## Impact
- Pages will render with default browser styling.

## Testing
- Manual smoke check in browser if desired; no automated tests.

## Rollback
- Revert the commit.

# Remove Web References Refactor Design

## Summary
Refactor the codebase to fully remove any references to the deleted `web/` directory. Clean up docs, scripts, and dependencies so the project focuses only on CLI/TUI/backend functionality.

## Goals
- Remove all references to `web/` and frontend workflows.
- Keep documentation aligned with the remaining CLI/TUI/backend features.
- Clean dependency lists so frontend tooling is no longer mentioned.

## Non-Goals
- No feature changes to backend/CLI/TUI beyond removing stale references.
- No new functionality added.

## Scope
- README updates: remove frontend instructions and references.
- Docs cleanup: remove any web-related guides or screenshots.
- Scripts cleanup: remove frontend-related scripts.
- Dependencies: remove frontend tooling or node references if present.

## Approach
- Search for `web/`, `frontend`, `Next.js`, and similar mentions across the repo.
- Delete or rewrite sections that reference web UI.
- Verify `pyproject.toml` and `requirements.txt` do not mention frontend tooling.

## Testing
- No new tests required.
- Ensure Python tests still run if requested.


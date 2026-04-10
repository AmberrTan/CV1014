# Remove UI Folder References Refactor Design

## Summary
Refactor the codebase to fully remove any references to the deleted UI directory. Clean up docs, scripts, and dependencies so the project focuses only on CLI/TUI/backend functionality.

## Goals
- Remove all references to the deleted UI directory and browser-based workflows.
- Keep documentation aligned with the remaining CLI/TUI/backend features.
- Clean dependency lists so browser UI tooling is no longer mentioned.

## Non-Goals
- No feature changes to backend/CLI/TUI beyond removing stale references.
- No new functionality added.

## Scope
- README updates: remove browser UI instructions and references.
- Docs cleanup: remove any browser UI guides or screenshots.
- Scripts cleanup: remove browser UI-related scripts.
- Dependencies: remove browser UI tooling references if present.

## Approach
- Search for UI-directory, browser UI, and JS tooling mentions across the repo.
- Delete or rewrite sections that reference the removed UI layer.
- Verify `pyproject.toml` and `requirements.txt` do not mention browser UI tooling.

## Testing
- No new tests required.
- Ensure Python tests still run if requested.

# Unused Code Cleanup Design

## Goal
Remove unused files, classes, and fields to simplify the codebase without changing current behavior or public API responses.

## Scope
- Delete unused module `src/osm_quality.py`.
- Remove unused model classes `UserQuery` and `RecommendationResponse` from `src/models.py`.
- Remove unused field `prefers_less_crowded` from `UserProfile` in `src/models.py`.
- Remove unused import `Field` from `src/models.py`.

## Non-Goals
- No new functionality or behavior changes.
- No refactors beyond the unused-code removal.
- No changes to API routes or response structures beyond removing unused model definitions.

## Approach
1. Confirm no references exist in `src/`, `tests/`, `docs/`, and `README.md`.
2. Delete `src/osm_quality.py`.
3. Update `src/models.py` to remove unused classes, field, and import.
4. Re-scan the repo to ensure no dangling references remain.

## Impact
- Smaller code surface and fewer unused definitions.
- No runtime behavior changes expected.

## Testing
- No tests required, but a quick `rg` scan will confirm no remaining references.

## Rollback
- Revert the commit if any missing references are discovered after removal.

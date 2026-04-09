# Remove Recommend/Admin Features (Design)

Date: 2026-04-09

## Goal
Simplify the application for a Year 1 course presentation by fully removing the recommend and admin features across frontend and backend, while keeping search and compare intact.

## Scope
In scope:
- Remove recommend and admin pages from the web frontend.
- Remove recommend and admin API endpoints and related backend services.
- Remove recommendation logic, data structures, and UI flows tied exclusively to recommend/admin.
- Remove tests that cover recommend/admin behavior.

Out of scope:
- Search and compare features (must remain functional).
- Unrelated enrichment/import utilities.

## Architecture Changes
- Frontend routes for `/recommend` and `/admin` will be removed entirely.
- Navigation and landing page CTAs pointing to recommend/admin will be removed.
- Backend API will drop the `/api/recommend` endpoint and its request/response models.
- Recommendation computation and any admin-related service helpers will be removed.
- Any UI layers (console or web) that invoke recommendation flow will be removed.

## Components and Responsibilities
Frontend (Next.js):
- Delete `web/app/recommend/page.tsx` and `web/app/admin/page.tsx`.
- Remove recommend/admin links from `web/app/layout.tsx` and `web/app/page.tsx`.
- Remove `web/components/admin-form.tsx` and any recommend-specific UI usage.
- Update `web/lib/api.ts` and `web/lib/types.ts` to remove recommend calls and fields.
- Remove recommendation-related display elements (score/reason) from shared components (e.g., gym cards or compare tables) if they are not used by search/compare.

Backend (FastAPI + services):
- Remove `/api/recommend` route and handler from `src/gym_recommender/api.py`.
- Remove request/response models in `src/gym_recommender/api_models.py` that are only for recommendations.
- Remove recommendation logic and helpers from `src/gym_recommender/recommendation.py` and corresponding service wrappers in `src/gym_recommender/services.py`.
- Remove console recommendation flow from `src/gym_recommender/ui.py` if it is no longer desired.
- Keep search and compare services/handlers intact.

## Data Flow Impact
- The search and compare flow remains unchanged.
- All recommendation data flow paths (input prefs → scoring → response payload) are removed.
- Any API response fields that exist solely for recommendation (e.g., `recommendation_score`, `recommendation_reason`) are removed.

## Error Handling
- No new error cases introduced; removal eliminates recommend/admin paths.
- Any callers expecting recommend/admin will be removed, so missing endpoint errors should not occur in normal use.

## Testing Plan
- Delete recommend/admin-specific tests in `tests/test_app.py` and any other suites.
- Ensure search and compare tests still run and pass.
- If any shared tests assume recommendation fields in payloads, adjust or remove those assertions.

## Acceptance Criteria
- Web app has no recommend/admin routes or navigation links.
- Backend exposes no recommend/admin endpoints.
- Search and compare features continue to work.
- Test suite passes without recommend/admin coverage.

## Risks and Mitigations
- Risk: Recommendation fields used implicitly in shared UI components.
  - Mitigation: Audit shared components and remove or guard recommend-only fields.
- Risk: Tests or types rely on recommendation payloads.
  - Mitigation: Update types and tests to align with new payloads.

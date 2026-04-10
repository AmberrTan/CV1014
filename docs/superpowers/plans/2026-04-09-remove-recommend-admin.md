# Remove Recommend/Admin Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fully remove recommend and admin features from frontend and backend while preserving search and compare.

**Architecture:** Delete recommend/admin routes and UI, remove recommend endpoint/models/services, and clean shared types/components to eliminate recommendation fields. Add a single backend test that asserts the recommend endpoint is gone.

**Tech Stack:** Python (FastAPI), Next.js (React), pytest

---

## File Structure (Targeted Changes)

Frontend:
- Delete: `web/app/recommend/page.tsx`
- Delete: `web/app/admin/page.tsx`
- Delete: `web/components/admin-form.tsx`
- Modify: `web/app/layout.tsx` (remove nav links)
- Modify: `web/app/page.tsx` (remove CTA to recommend/admin)
- Modify: `web/lib/api.ts` (remove recommend API helper)
- Modify: `web/lib/types.ts` (remove recommendation fields)
- Modify: `web/components/gym-card.tsx` (remove recommendation score/reason display)
- Modify: `web/components/compare-table.tsx` (remove recommendation score column)

Backend:
- Modify: `src/gym_recommender/api.py` (remove `/api/recommend` route)
- Modify: `src/gym_recommender/api_models.py` (remove recommendation request/response models)
- Modify: `src/gym_recommender/services.py` (remove recommendation service functions)
- Delete: `src/gym_recommender/recommendation.py`
- Modify: `src/gym_recommender/ui.py` (remove recommendation console flow/menu item)
- Modify: `tests/test_app.py` (remove recommendation tests, add 404 test)

---

## Chunk 1: Backend Recommendation Removal

### Task 1: Add failing test for removed recommend endpoint

**Files:**
- Modify: `tests/test_app.py`

- [ ] **Step 1: Write the failing test**

```python
def test_api_recommend_is_removed(self) -> None:
    client = _create_client()
    response = client.post("/api/recommend", json={"preferred_area": "Raffles Place"})
    self.assertEqual(response.status_code, 404)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_app.py::GymSystemTests::test_api_recommend_is_removed -v`
Expected: FAIL with status code 200 (endpoint still exists).

- [ ] **Step 3: Commit**

```bash
git add tests/test_app.py
git commit -m "test: assert recommend endpoint removed"
```

### Task 2: Remove recommend endpoint and models

**Files:**
- Modify: `src/gym_recommender/api.py`
- Modify: `src/gym_recommender/api_models.py`

- [ ] **Step 1: Remove recommend route handler**
  - Delete the `/api/recommend` route function and related imports.

- [ ] **Step 2: Remove recommendation request/response models**
  - Delete models used only by recommendation endpoints.
  - Update any exports or references.

- [ ] **Step 3: Run test to verify it passes**

Run: `uv run pytest tests/test_app.py::GymSystemTests::test_api_recommend_is_removed -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add src/gym_recommender/api.py src/gym_recommender/api_models.py
git commit -m "feat: remove recommend api endpoint and models"
```

### Task 3: Remove recommendation services and logic

**Files:**
- Modify: `src/gym_recommender/services.py`
- Delete: `src/gym_recommender/recommendation.py`
- Modify: `src/gym_recommender/ui.py`

- [ ] **Step 1: Remove recommendation services**
  - Delete `recommend_gym_records` and any recommendation-specific helpers.
  - Remove imports of recommendation logic and any recommendation-only fields.

- [ ] **Step 2: Remove console recommendation flow**
  - Remove menu items and functions tied to recommendation in the console UI.

- [ ] **Step 3: Run focused backend tests**

Run: `uv run pytest tests/test_app.py -v`
Expected: PASS for search/compare tests; recommend tests should be removed.

- [ ] **Step 4: Commit**

```bash
git add src/gym_recommender/services.py src/gym_recommender/ui.py src/gym_recommender/recommendation.py tests/test_app.py
git commit -m "feat: remove recommendation services and console flow"
```

---

## Chunk 2: Frontend Recommend/Admin Removal

### Task 4: Remove recommend/admin pages and navigation

**Files:**
- Delete: `web/app/recommend/page.tsx`
- Delete: `web/app/admin/page.tsx`
- Modify: `web/app/layout.tsx`
- Modify: `web/app/page.tsx`

- [ ] **Step 1: Delete recommend/admin pages**

- [ ] **Step 2: Remove nav links and CTA references**
  - Remove links in layout and homepage pointing to recommend/admin.

- [ ] **Step 3: Commit**

```bash
git add web/app/recommend/page.tsx web/app/admin/page.tsx web/app/layout.tsx web/app/page.tsx
git commit -m "feat: remove recommend/admin pages and navigation"
```

### Task 5: Remove admin component and recommend API/types usage

**Files:**
- Delete: `web/components/admin-form.tsx`
- Modify: `web/lib/api.ts`
- Modify: `web/lib/types.ts`
- Modify: `web/components/gym-card.tsx`
- Modify: `web/components/compare-table.tsx`

- [ ] **Step 1: Remove recommend API helper**
  - Delete the `recommendGyms` API function and related payload types.

- [ ] **Step 2: Remove recommendation fields from shared types**
  - Remove `recommendation_score` and `recommendation_reason`.

- [ ] **Step 3: Remove recommendation display from shared UI**
  - Remove match score display from gym cards.
  - Remove recommendation score column from compare table.

- [ ] **Step 4: Commit**

```bash
git add web/components/admin-form.tsx web/lib/api.ts web/lib/types.ts web/components/gym-card.tsx web/components/compare-table.tsx
git commit -m "feat: remove recommend/admin frontend support"
```

---

## Chunk 3: Cleanup and Verification

### Task 6: Remove obsolete tests and run full suite

**Files:**
- Modify: `tests/test_app.py`

- [ ] **Step 1: Remove recommend-specific tests**
  - Delete test cases that exercise recommendation scoring and `/api/recommend` behavior.

- [ ] **Step 2: Run full test suite**

Run: `uv run pytest -v`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_app.py
git commit -m "test: remove recommend coverage"
```

---

## Notes
- Keep search and compare behavior unchanged.
- Ensure no lingering references to recommendation fields in frontend types or UI.
- If any lints or TypeScript errors appear, fix them in the same commit as their source change.

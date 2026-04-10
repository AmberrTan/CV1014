# TUI Area Partial Match (Substring) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add case-insensitive substring matching for area input in the Textual TUI, showing all matches when ambiguous and preventing search in that case.

**Architecture:** Extract a small area-resolution helper that maps a raw input string to a single canonical area or a user-facing message, then wire it into the search flow before filtering. Keep search filtering unchanged.

**Tech Stack:** Python, Textual, pytest

---

## File Structure
- Modify: `/Users/zhoufuwang/Projects/CV1014/src/gym_recommender/tui.py` (add a reusable area resolver and use it in search flow)
- Modify or Create: `/Users/zhoufuwang/Projects/CV1014/tests/test_tui.py` or `/Users/zhoufuwang/Projects/CV1014/tests/test_tui_area.py` (unit tests for resolver)

### Task 1: Add Tests for Area Resolver

**Files:**
- Create: `/Users/zhoufuwang/Projects/CV1014/tests/test_tui_area.py`

- [ ] **Step 1: Write failing tests**

```python
from gym_recommender.tui import resolve_area_match


def test_resolve_area_single_match_substring() -> None:
    areas = ["Jurong East", "Bedok"]
    match, message = resolve_area_match("Jurong", areas)
    assert match == "Jurong East"
    assert message == "Using area 'Jurong East' for 'Jurong'."


def test_resolve_area_multiple_matches() -> None:
    areas = ["Jurong East", "Paya Lebar", "Bedok"]
    match, message = resolve_area_match("a", areas)
    assert match is None
    assert message == "Area 'a' matches multiple areas: Jurong East, Paya Lebar."


def test_resolve_area_no_match() -> None:
    areas = ["Jurong East", "Bedok"]
    match, message = resolve_area_match("Unknown", areas)
    assert match is None
    assert message == "Area 'Unknown' not found. Try: Jurong East, Bedok."
```

- [ ] **Step 2: Run tests to confirm failure**

Run: `uv run pytest -v /Users/zhoufuwang/Projects/CV1014/tests/test_tui_area.py`

Expected: FAIL with `ImportError` or `AttributeError` because `resolve_area_match` is not defined yet.

### Task 2: Implement Area Resolver and Wire Into Search

**Files:**
- Modify: `/Users/zhoufuwang/Projects/CV1014/src/gym_recommender/tui.py`

- [ ] **Step 1: Add helper function**

Add near other helpers:

```python
def resolve_area_match(raw_area: str, areas: list[str]) -> tuple[str | None, str | None]:
    cleaned = raw_area.strip()
    if not cleaned:
        return None, None
    lowered = cleaned.casefold()
    for area in areas:
        if area.casefold() == lowered:
            return area, None
    partial_matches = [area for area in areas if lowered in area.casefold()]
    if len(partial_matches) == 1:
        return partial_matches[0], f"Using area '{partial_matches[0]}' for '{cleaned}'."
    if not partial_matches:
        return None, f"Area '{cleaned}' not found. Try: {', '.join(areas)}."
    return None, f"Area '{cleaned}' matches multiple areas: {', '.join(partial_matches)}."
```

- [ ] **Step 2: Use helper in `SearchScreen._run_search`**

Replace the local resolver logic with:

```python
raw_area = self.query_one("#search-area", Input).value
resolved_area, area_message = resolve_area_match(raw_area, self.app.get_areas())
if raw_area.strip() and not resolved_area:
    status.update(area_message or "Please enter a valid area.")
    results_view.clear()
    return
if resolved_area:
    filters["area"] = resolved_area
```

- [ ] **Step 3: Run the tests again**

Run: `uv run pytest -v /Users/zhoufuwang/Projects/CV1014/tests/test_tui_area.py`

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add /Users/zhoufuwang/Projects/CV1014/src/gym_recommender/tui.py \
        /Users/zhoufuwang/Projects/CV1014/tests/test_tui_area.py

git commit -m "feat: support substring area matching in TUI"
```

### Task 3: Optional Full Test Suite

**Files:**
- Test: `/Users/zhoufuwang/Projects/CV1014/tests`

- [ ] **Step 1: Run full test suite (optional)**

Run: `uv run pytest -v`

Expected: PASS

---

## Plan Self-Review
- Spec coverage: Area substring matching, disambiguation messaging, no search on ambiguous/no match — covered in Tasks 1–2.
- Placeholder scan: No TODOs or vague steps.
- Type consistency: `resolve_area_match` signature matches tests and usage.


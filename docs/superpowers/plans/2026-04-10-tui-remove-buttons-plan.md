# TUI Remove Buttons Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the Search and Compare buttons from the Textual TUI and rely exclusively on Enter key submission.

**Architecture:** Adjust the TUI screen compositions to drop the button widgets and delete their event handlers. Preserve Input.Submitted handlers to keep Enter‑only behavior.

**Tech Stack:** Python, Textual

---

## File Structure
- Modify: `/Users/zhoufuwang/Projects/CV1014/src/gym_recommender/tui.py`

### Task 1: Remove TUI Buttons and Handlers

**Files:**
- Modify: `/Users/zhoufuwang/Projects/CV1014/src/gym_recommender/tui.py`

- [ ] **Step 1: Remove Search button from Search screen compose**

Delete the `Button("Search", ...)` line from the Search screen layout.

- [ ] **Step 2: Remove Compare button from Compare screen compose**

Delete the `Button("Compare", ...)` line from the Compare screen layout.

- [ ] **Step 3: Remove button pressed handlers**

Delete the `on_button_pressed` methods in `SearchScreen` and `CompareScreen` (they are no longer used once the buttons are removed).

- [ ] **Step 4: Verify Enter behavior unchanged**

Manually run the TUI and confirm Enter still triggers search/compare:

Run: `uv run gym-recommender-tui`

Expected:
- Enter in any search input triggers search.
- Enter in the compare IDs input triggers compare.

- [ ] **Step 5: Commit**

```bash
git add /Users/zhoufuwang/Projects/CV1014/src/gym_recommender/tui.py

git commit -m "feat: remove TUI search/compare buttons"
```

---

## Plan Self-Review
- Spec coverage: removes buttons, keeps Enter handlers — covered.
- Placeholder scan: no TODOs.
- Type consistency: no new types.


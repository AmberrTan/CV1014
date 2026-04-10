# TUI Demo Tightening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tighten the repo to only the Textual TUI runtime and the OpenStreetMap ingestion pipeline that overwrites `data/gyms.json` by default.

**Architecture:** Keep TUI runtime modules + OSM import/enrichment modules; remove any non-demo artifacts and unnecessary docs/tests. Simplify `data.py` to always use `data/gyms.json` and adjust the OSM import script to default to that path while retaining `--output` for overrides.

**Tech Stack:** Python, Textual, pytest

---

## File Structure
- Create: `/Users/zhoufuwang/Projects/CV1014/tests/test_data_defaults.py`
- Modify: `/Users/zhoufuwang/Projects/CV1014/src/gym_recommender/data.py`
- Modify: `/Users/zhoufuwang/Projects/CV1014/scripts/import_osm_gyms.py`
- Modify: `/Users/zhoufuwang/Projects/CV1014/README.md`
- Delete: `/Users/zhoufuwang/Projects/CV1014/docs/superpowers/` (entire directory)
- Delete: `/Users/zhoufuwang/Projects/CV1014/system_flowchart.drawio`
- Delete: `/Users/zhoufuwang/Projects/CV1014/CV1014_AY25S2_mini_project.pdf`
- Delete: `/Users/zhoufuwang/Projects/CV1014/Appendix 1_Program assessment rubrics.docx`

---

### Task 1: Lock Default Dataset Path (TDD)

**Files:**
- Create: `/Users/zhoufuwang/Projects/CV1014/tests/test_data_defaults.py`
- Modify: `/Users/zhoufuwang/Projects/CV1014/src/gym_recommender/data.py`

- [ ] **Step 1: Write failing test for default dataset path**

```python
from __future__ import annotations

import importlib
from pathlib import Path

import gym_recommender.data as data


def test_default_database_path_ignores_env_override(monkeypatch) -> None:
    monkeypatch.setenv("GYM_DATABASE_PATH", "data/other.json")
    importlib.reload(data)

    expected = data.ROOT_DIR / "data/gyms.json"
    assert data.DEFAULT_DATABASE_PATH == expected

    monkeypatch.delenv("GYM_DATABASE_PATH", raising=False)
    importlib.reload(data)
```

- [ ] **Step 2: Run the new test to confirm it fails**

Run: `uv run pytest -q tests/test_data_defaults.py`

Expected: FAIL because `DEFAULT_DATABASE_PATH` currently respects `GYM_DATABASE_PATH`.

- [ ] **Step 3: Update `data.py` to always use `data/gyms.json`**

```python
"""Read/write helpers for the gym JSON database."""

from __future__ import annotations

import json
from pathlib import Path

from gym_recommender.config import ROOT_DIR
from gym_recommender.models import GymRecord

DEFAULT_DATABASE_PATH = ROOT_DIR / "data/gyms.json"
```

- [ ] **Step 4: Re-run the test**

Run: `uv run pytest -q tests/test_data_defaults.py`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add /Users/zhoufuwang/Projects/CV1014/tests/test_data_defaults.py \
        /Users/zhoufuwang/Projects/CV1014/src/gym_recommender/data.py

git commit -m "test: lock default dataset path"
```

---

### Task 2: Simplify OSM Import Defaults

**Files:**
- Modify: `/Users/zhoufuwang/Projects/CV1014/scripts/import_osm_gyms.py`

- [ ] **Step 1: Update default output path to `data/gyms.json`**

```python
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/gyms.json"),
        help="Output JSON file for the imported gyms (defaults to data/gyms.json).",
    )
```

- [ ] **Step 2: Commit**

```bash
git add /Users/zhoufuwang/Projects/CV1014/scripts/import_osm_gyms.py

git commit -m "chore: default OSM import output to gyms.json"
```

---

### Task 3: Tighten README to Demo-Only Flow

**Files:**
- Modify: `/Users/zhoufuwang/Projects/CV1014/README.md`

- [ ] **Step 1: Update import section to emphasize default overwrite**

```markdown
## Data Import (OpenStreetMap)

    uv run python scripts/import_osm_gyms.py --limit 100

Use `--output` to write elsewhere:

    uv run python scripts/import_osm_gyms.py --limit 100 --output data/gyms_osm_sg.json
```

- [ ] **Step 2: Commit**

```bash
git add /Users/zhoufuwang/Projects/CV1014/README.md

git commit -m "docs: focus README on demo ingestion flow"
```

---

### Task 4: Remove Non-Demo Artifacts

**Files:**
- Delete: `/Users/zhoufuwang/Projects/CV1014/docs/superpowers/`
- Delete: `/Users/zhoufuwang/Projects/CV1014/system_flowchart.drawio`
- Delete: `/Users/zhoufuwang/Projects/CV1014/CV1014_AY25S2_mini_project.pdf`
- Delete: `/Users/zhoufuwang/Projects/CV1014/Appendix 1_Program assessment rubrics.docx`

- [ ] **Step 1: Remove unused docs and artifacts**

```bash
rm -rf /Users/zhoufuwang/Projects/CV1014/docs/superpowers
rm -f /Users/zhoufuwang/Projects/CV1014/system_flowchart.drawio
rm -f /Users/zhoufuwang/Projects/CV1014/CV1014_AY25S2_mini_project.pdf
rm -f "/Users/zhoufuwang/Projects/CV1014/Appendix 1_Program assessment rubrics.docx"
```

- [ ] **Step 2: Commit**

```bash
git add -A

git commit -m "chore: remove non-demo artifacts"
```

---

### Task 5: Full Test Pass

- [ ] **Step 1: Run test suite**

Run: `uv run pytest -q`

Expected: PASS

- [ ] **Step 2: Commit (if needed)**

```bash
git status --short
```

If any changes remain, commit them with an appropriate message.

---

## Plan Self-Review
- Spec coverage: All scope items mapped to Tasks 1–4 with tests in Task 5.
- Placeholder scan: No TODOs or vague steps.
- Type consistency: Paths and module references match current repo structure.

# Remove UI Folder References Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove all references to the deleted UI directory and clean the codebase to focus on CLI/TUI/backend only.

**Architecture:** No architecture changes; this is a cleanup pass to remove stale docs/scripts/dependencies that referenced the removed UI layer.

**Tech Stack:** Python, Textual

---

## File Structure
- Modify: `/Users/zhoufuwang/Projects/CV1014/README.md`
- Modify: `/Users/zhoufuwang/Projects/CV1014/docs/**` (any UI-related docs)
- Modify: `/Users/zhoufuwang/Projects/CV1014/scripts/**` (any UI-related scripts)
- Modify: `/Users/zhoufuwang/Projects/CV1014/pyproject.toml`
- Modify: `/Users/zhoufuwang/Projects/CV1014/requirements.txt`
- Modify: `/Users/zhoufuwang/Projects/CV1014/system_flowchart.drawio`

### Task 1: Locate and Remove UI References

**Files:**
- Modify: `/Users/zhoufuwang/Projects/CV1014/README.md`
- Modify: `/Users/zhoufuwang/Projects/CV1014/docs/**`
- Modify: `/Users/zhoufuwang/Projects/CV1014/scripts/**`
- Modify: `/Users/zhoufuwang/Projects/CV1014/system_flowchart.drawio`

- [ ] **Step 1: Find all UI references**

Run:
```bash
rg -n "ui directory|browser ui|ui layer|js tooling" /Users/zhoufuwang/Projects/CV1014
```

- [ ] **Step 2: Update README**

Remove any sections that refer to the removed UI layer or JS tooling. Keep CLI/TUI instructions intact.

- [ ] **Step 3: Update docs**

Delete or rewrite any documents or sections that mention the removed UI layer.

- [ ] **Step 4: Update scripts**

Remove references to browser UI scripts, or delete obsolete scripts if they are only for the removed UI layer.

- [ ] **Step 5: Update system diagram**

Remove the UI box and any UI references from `system_flowchart.drawio` so the diagram reflects the current CLI/TUI/backend architecture.

- [ ] **Step 6: Commit**

```bash
git add /Users/zhoufuwang/Projects/CV1014/README.md \
        /Users/zhoufuwang/Projects/CV1014/docs \
        /Users/zhoufuwang/Projects/CV1014/scripts \
        /Users/zhoufuwang/Projects/CV1014/system_flowchart.drawio

git commit -m "refactor: remove UI references from docs and scripts"
```

### Task 2: Clean Dependencies

**Files:**
- Modify: `/Users/zhoufuwang/Projects/CV1014/pyproject.toml`
- Modify: `/Users/zhoufuwang/Projects/CV1014/requirements.txt`

- [ ] **Step 1: Remove JS tooling references**

Remove any JS tooling notes or references that are no longer used.

- [ ] **Step 2: Commit**

```bash
git add /Users/zhoufuwang/Projects/CV1014/pyproject.toml \
        /Users/zhoufuwang/Projects/CV1014/requirements.txt

git commit -m "chore: remove stale UI dependency references"
```

### Task 3: Optional Test Run

- [ ] **Step 1: Run tests (optional)**

Run: `uv run pytest -v`

Expected: PASS

---

## Plan Self-Review
- Spec coverage: README/docs/scripts/diagram/deps cleanup covered in Tasks 1–2.
- Placeholder scan: no TODOs.
- Type consistency: no new code types.

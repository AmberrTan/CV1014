# Strip HTML CSS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove all CSS (inline, `<style>` blocks, and linked stylesheets) from the static HTML pages.

**Architecture:** A direct content edit of the static HTML files; no JS or API changes.

**Tech Stack:** HTML

---

## File Structure
- Modify: `/Users/zhoufuwang/Projects/cv1014_2/src/static/index.html`
- Modify: `/Users/zhoufuwang/Projects/cv1014_2/src/static/profile.html`

### Task 1: Strip CSS from `index.html`

**Files:**
- Modify: `/Users/zhoufuwang/Projects/cv1014_2/src/static/index.html`

- [ ] **Step 1: Remove `<style>` block**

Delete the entire `<style>...</style>` block in the `<head>`.

- [ ] **Step 2: Remove inline styles**

Remove all `style="..."` attributes in the file, including the inline styles in the `<h2>` and error/loading messages.

- [ ] **Step 3: Commit**

```bash
git add /Users/zhoufuwang/Projects/cv1014_2/src/static/index.html

git commit -m "Strip CSS from index.html"
```

### Task 2: Strip CSS from `profile.html`

**Files:**
- Modify: `/Users/zhoufuwang/Projects/cv1014_2/src/static/profile.html`

- [ ] **Step 1: Remove `<style>` block**

Delete the entire `<style>...</style>` block in the `<head>`.

- [ ] **Step 2: Remove inline styles**

Remove all `style="..."` attributes (e.g., on the search-message container).

- [ ] **Step 3: Commit**

```bash
git add /Users/zhoufuwang/Projects/cv1014_2/src/static/profile.html

git commit -m "Strip CSS from profile.html"
```

### Task 3: Final sanity check

- [ ] **Step 1: Quick grep for remaining styles**

```bash
rg -n "<style|stylesheet|style=\"" /Users/zhoufuwang/Projects/cv1014_2/src/static
```
Expected: no matches.

- [ ] **Step 2: Commit**

```bash
git status -sb
```
Expected: clean working tree.


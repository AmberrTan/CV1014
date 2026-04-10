# Compare Button Height Alignment Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Compare button exactly match the Gym IDs input height (including borders) on the compare page across all breakpoints.

**Architecture:** Add a compare-toolbar modifier class that defines a shared height token, then apply that height to the input and Compare button within the compare page toolbar only.

**Tech Stack:** Next.js, React, global CSS

---

## File Structure (Targeted Changes)
- Modify: `web/app/compare/page.tsx` (add compare toolbar class)
- Modify: `web/app/globals.css` (define height token and apply to compare toolbar input/button)

---

## Chunk 1: Height Alignment Styles

### Task 1: Add compare-toolbar height token and apply to input/button

**Files:**
- Modify: `web/app/globals.css`

- [ ] **Step 1: Write the failing test**

No automated tests for CSS-only height alignment. Skip test creation.

- [ ] **Step 2: Write minimal implementation**

Add styles scoped to compare toolbar:

```css
.toolbar--compare {
  --compare-field-height: 48px;
}

.toolbar--compare .field input {
  height: var(--compare-field-height);
}

.toolbar--compare .button {
  height: var(--compare-field-height);
}
```

- [ ] **Step 3: Commit**

```bash
git add web/app/globals.css
git commit -m "style: align compare input and button heights"
```

### Task 2: Apply compare toolbar class in compare page

**Files:**
- Modify: `web/app/compare/page.tsx`

- [ ] **Step 1: Write the failing test**

No automated tests for UI alignment. Skip test creation.

- [ ] **Step 2: Write minimal implementation**

Update the form class:

```tsx
<form className="toolbar toolbar--baseline toolbar--compare" ...>
```

- [ ] **Step 3: Run lint**

Run: `npm -C web run lint`
Expected: no errors (note if the existing lint config fails).

- [ ] **Step 4: Commit**

```bash
git add web/app/compare/page.tsx
git commit -m "feat: match compare button height to input"
```

---

## Chunk 2: Verification

### Task 3: Manual spot-check

**Files:**
- None

- [ ] **Step 1: Visual check**

Run: `npm -C web run dev` and open `/compare`.
Expected: input and Compare button are exactly the same height across breakpoints.

- [ ] **Step 2: Commit (optional)**

No code changes expected.

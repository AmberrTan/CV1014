# Compare Button Alignment Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Compare button on the compare page smaller and aligned to the input field baseline.

**Architecture:** Add a compact button variant and a baseline-aligned toolbar modifier in the global CSS, then apply both on the compare page form.

**Tech Stack:** Next.js, React, global CSS

---

## File Structure (Targeted Changes)
- Modify: `web/app/compare/page.tsx` (apply classes)
- Modify: `web/app/globals.css` (add `toolbar--baseline` and `button--small` styles)

---

## Chunk 1: Compare Toolbar Alignment

### Task 1: Add baseline alignment and compact button styles

**Files:**
- Modify: `web/app/globals.css`

- [ ] **Step 1: Write the failing test**

No automated test is available for CSS-only adjustments. Skip test creation.

- [ ] **Step 2: Write minimal implementation**

Add the following styles:

```css
.toolbar--baseline {
  align-items: baseline;
}

.button--small {
  padding: 8px 18px;
  font-size: 0.9rem;
}
```

- [ ] **Step 3: Commit**

```bash
git add web/app/globals.css
git commit -m "style: add baseline toolbar and small button"
```

### Task 2: Apply baseline toolbar and compact button on compare page

**Files:**
- Modify: `web/app/compare/page.tsx`

- [ ] **Step 1: Write the failing test**

No automated test is available for layout alignment. Skip test creation.

- [ ] **Step 2: Write minimal implementation**

Update the form and button classes:

```tsx
<form className="toolbar toolbar--baseline" ...>
  ...
  <button className="button button--small" ...>
    Compare
  </button>
</form>
```

- [ ] **Step 3: Run lint**

Run: `npm -C web run lint`
Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add web/app/compare/page.tsx
git commit -m "feat: align compare button with input baseline"
```

---

## Chunk 2: Verification

### Task 3: Manual sanity check

**Files:**
- None

- [ ] **Step 1: Visual spot-check**

Run: `npm -C web run dev` and open `/compare`.
Expected: Compare button is smaller and aligns with the input baseline.

- [ ] **Step 2: Commit (optional)**

No code changes expected; no commit required.

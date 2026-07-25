# Design & Development Scratchpad

## Guiding Principle

**This site must adhere 100% to the Material Design 3 specification.**

All design decisions — layout, typography, colour, spacing, motion, and components —
must be validated against the official M3 spec pages below before implementation.

### M3 Spec Reference Links

| Topic | URL |
|-------|-----|
| Scaffold / Layout overview | https://m3.material.io/foundations/layout/scaffold/overview |
| Grids & Spacing | https://m3.material.io/foundations/layout/grids-spacing/overview |
| Colour system | https://m3.material.io/styles/color/system/overview |
| Typography | https://m3.material.io/styles/typography/overview |
| UX Writing / Style guide | https://m3.material.io/foundations/content-design/style-guide/ux-writing-best-practices |
| Navigation Drawer | https://m3.material.io/components/navigation-drawer/specs |
| Navigation Rail | https://m3.material.io/components/navigation-rail/specs |
| Navigation Bar (bottom) | https://m3.material.io/components/navigation-bar/specs |
| Cards | https://m3.material.io/components/cards/specs |
| Buttons | https://m3.material.io/components/buttons/specs |
| Chips | https://m3.material.io/components/chips/specs |

---

## Progress Log

### Phase 0 — Original State
- Hugo site with m10c theme
- Apple Glass / glassmorphism design with backdrop-blur, gradient backgrounds
- No design system, hardcoded colours throughout
- Tag: `v1.0-stable`

---

### Phase 1 — Initial M3 Migration (commit `1e7fca1`)
**What was done:**
- Replaced glassmorphism with flat M3 surfaces
- Added CSS custom property tokens for colour, shape, motion
- Built M3 Navigation Drawer (desktop)
- Built M3 Bottom Navigation Bar (mobile < 600px)
- Post cards as M3 Elevated Cards
- M3 Ripple effect (Web Animations API)
- View transitions (page-to-page morph)
- Floating sticky ToC for post pages (desktop >= 1280px)
- Dark / light theme toggle with localStorage persistence
- Active nav highlight via JS
- Floating sidebar toggle button for post pages

**Problems that occurred during this phase:**
- Apostrophes in SCSS comments (`Amro's`, `doesn't`) broke Dart Sass via SSH heredoc corruption
- `_base.scss` was not stubbed — m10c's 1345-line Glass stylesheet kept overriding M3 rules
- Python string surgery on large SCSS blocks corrupted content multiple times
- Deployed broken CSS twice before root cause found

**Lesson learned:** Never write large SCSS via SSH heredoc or Python string replacement.
Always write to a local temp file and copy. Verify brace balance and quote parity before every commit.

- Tag: `stable-pre-m3-full` at `8850ef6` (last known good state before full rewrite)

---

### Phase 2 — Claude Colour Palette + Inter Font (commit `179b8ad`)
**What was done:**
- Replaced neutral greyscale palette with Claude's exact CDS (Claude Design System) colours
  extracted directly from claude.ai's live CSS (`c6a992d55-dpf7G8XJ.css`)
- Light surfaces: warm grey (#F9F9F7, #F3F3F0, #EDECE8, #E7E6E1)
- Dark surfaces: near-black (#131313, #1C1C1B, #20201F, #2C2C2A)
- Primary accent: Claude orange / clay `#D97757` — used ONLY on container backgrounds,
  never as text colour (contrast ratio too low on light backgrounds)
- Replaced Roboto with **Inter** (variable font 300–700) — closest open-source match
  to Anthropic Sans, used by Claude's design team as the reference before commissioning
  their proprietary font
- Kept **JetBrains Mono** for all code blocks
- Drawer: "Amro's Blog" headline, removed tagline / description / tag chips
- Drawer: footer sticks to bottom (flex column layout)
- Drawer: social icons as M3 icon buttons in footer
- Active nav: switched to `primary-container` + `on-primary-container`
- `<header>` changed to `<nav aria-label="Main navigation">` (semantic fix)
- Skip-to-main-content link added (M3 accessibility requirement)
- `:focus-visible` ring added (3px solid primary, offset 2px) on all interactive elements

- Tag: `stable-M3-Claude-Color` at `179b8ad`

---

### Phase 3 — Full M3 Spec Compliance: Typescale, Layout, Nav Rail (commit `32aa951`)
**What was done:**

**Typography — all 15 M3 type roles defined as CSS tokens:**
```
--md-type-display-large/medium/small-*
--md-type-headline-large/medium/small-*
--md-type-title-large/medium/small-*
--md-type-body-large/medium/small-*
--md-type-label-large/medium/small-*
```
Each token covers: size, line-height, weight, tracking (letter-spacing).

**Post headings mapped to M3 roles:**
- h2 = Headline Medium (1.75rem / 400wt / 2.25rem lh)
- h3 = Headline Small (1.5rem / 400wt / 2rem lh)
- h4 = Title Large (1.375rem / 400wt / 1.75rem lh)
- h5 = Title Medium (1rem / 500wt / 1.5rem lh)
- h6 = Title Small (0.875rem / 500wt / 1.25rem lh)

**M3 Scaffold breakpoints — now 100% spec:**
- Compact `< 600px` → Bottom Navigation Bar (80px, 4 items)
- Medium `600–839px` → Navigation Rail (80px wide, icon + label) — NEW
- Expanded `>= 840px` → Navigation Drawer (360px, persistent)

**Layout fixes:**
- Mobile padding: 1rem (16px) — was 0.9rem (off M3 compact grid)
- Tablet padding: 1.5rem (24px) — per M3 medium spec
- Drawer top padding: 0.5rem — was 2rem (spec says 8px)
- Card gap: 1rem (16px, 4dp grid) — was 0.75rem

**Accessibility:**
- Skip link (`<a class="m3-skip-link">`) shown on keyboard Tab
- All focus states visible (`:focus-visible`)
- `<main id="main-content">` as skip link target

---

### Phase 4 — Typography Precision + Bug Fixes (commit `48d20f3`)
**What was done:**

**Tracking (letter-spacing) units corrected — em → rem:**

The M3 spec expresses tracking in **absolute rem**, not relative em.
Source: `_md-sys-typescale.scss` v0.192 from material-components/material-web.

| Token | Was | Now (correct) |
|-------|-----|---------------|
| display-large-tracking | -0.016em | -0.015625rem |
| title-medium-tracking | 0.009em | 0.009375rem |
| title-small-tracking | 0.006em | 0.00625rem |
| body-large-tracking | 0.031em | 0.03125rem |
| body-medium-tracking | 0.016em | 0.015625rem |
| body-small-tracking | 0.025em | 0.025rem |
| label-large-tracking | 0.006em | 0.00625rem |
| label-medium-tracking | 0.031em | 0.03125rem |
| label-small-tracking | 0.031em | 0.03125rem |

**Bug fix — post card hover underline:**
- Root cause: `.post-card` is an `<a>` inside `<article>`, matched by the
  `body:not(.cv-page) .app-container article a { text-decoration: underline !important }` rule.
  Fix: added `.post-card` to the `text-decoration: none !important` exception list.

**Blog / Notes page title (h1) missing rule:**
- The `<h1>Blog</h1>` and `<h1>Notes</h1>` had no explicit M3 typescale rule,
  rendering at browser-default bold h1 (~2em bold). Added Display Small rule:
  `2.25rem / 400wt / 2.75rem line-height / 0 tracking`.

**_notes.scss — 12 fixes:**
- `notes-stream-title`: 1.75rem → Display Small (2.25rem) token
- `note-card-content`: color was `on-surface-variant` → corrected to `on-surface`
  (body reading text must be full contrast per M3 colour spec)
- All hardcoded font-size, font-weight, letter-spacing values replaced with M3 tokens

**_about.scss — 14 fixes:**
- `about-hero-role`: weight 600 → 500 (M3 Title Medium spec)
- All elements now use correct M3 type role tokens

---

## Current State (as of commit `48d20f3`)

### What is correct
- All 15 M3 type scale roles defined with exact spec values
- All tracking values in correct absolute rem units
- Claude CDS colour palette (light + dark) with clay orange primary
- M3 scaffold breakpoints (compact / medium / expanded)
- Navigation: Drawer (840px+), Rail (600–839px), Bottom Bar (<600px)
- Post headings h2–h6 all mapped to correct M3 roles
- Focus-visible rings on all interactive elements
- Skip navigation link
- Semantic HTML (`<nav>`, `<main>`, `<aside>`)
- Post card hover underline fixed
- Page titles (Blog, Notes) styled as Display Small
- Note card content text corrected to on-surface colour
- All hardcoded values in _notes.scss and _about.scss replaced with tokens

### Known remaining items
- `_notes.scss` timeline active state still uses `secondary-container` (should use `primary-container`)
- About page section headings (`<h2>` inside `.about-hero`) have no explicit M3 role
- No `prefers-reduced-motion` media query on animations
- No `color-scheme: light dark` declaration on `:root`
- CV page is deliberately excluded from M3 (preserved as-is)

---

## Safe File Modification Rules

1. **Never write large SCSS via SSH heredoc** — write to a temp file locally and copy
2. **Always verify before committing:**
   - Single quotes outside `/* */` comments must be even
   - `{` count must equal `}` count
   - No apostrophes in unquoted SCSS strings
3. **Never rewrite a working file from scratch** — use targeted Python string replacements
4. **One logical change per commit** — never pile multiple unverified changes together
5. **Always stage only the intended files** — check `git status` before `git commit`
6. **Test via CI** — Hugo is not installed on the deployment server; GitHub Actions builds on push

---

## Colour Reference

### Light Mode (Claude CDS)
| Role | Hex | Use |
|------|-----|-----|
| background | #F9F9F7 | Page background |
| surface | #F9F9F7 | Drawer, cards base |
| surface-container-low | #F3F3F0 | Card fills |
| surface-container | #EDECE8 | Code block backgrounds |
| surface-container-high | #E7E6E1 | Search bar, input |
| on-surface | #0B0B0B | Primary text |
| on-surface-variant | #6D6B67 | Secondary text, labels |
| outline | #A5A49A | Borders |
| outline-variant | #E1E0D9 | Subtle dividers |
| primary | #D97757 | Clay orange — containers only |
| primary-container | #FDEEE7 | Active nav indicator bg |
| on-primary-container | #3D1A0A | Active nav text |

### Dark Mode (Claude CDS)
| Role | Hex | Use |
|------|-----|-----|
| background | #131313 | Page background |
| surface-container-low | #1C1C1B | Card fills |
| surface-container | #20201F | Code blocks |
| surface-container-high | #2C2C2A | Search bar |
| on-surface | #F9F9F7 | Primary text |
| on-surface-variant | #C3C2B7 | Secondary text |
| primary | #D97757 | Same clay orange |
| primary-container | #5C3020 | Active nav indicator bg |
| on-primary-container | #FDEEE7 | Active nav text |

---

## Typography Quick Reference

| M3 Role | Size | Line-H | Weight | Tracking | Used for |
|---------|------|--------|--------|----------|---------|
| Display Small | 2.25rem | 2.75rem | 400 | 0 | Blog/Notes page title |
| Headline Large | 2rem | 2.5rem | 400 | 0 | Post title |
| Headline Medium | 1.75rem | 2.25rem | 400 | 0 | Post h2 |
| Headline Small | 1.5rem | 2rem | 400 | 0 | Post h3, Drawer headline |
| Title Large | 1.375rem | 1.75rem | 400 | 0 | Post h4 |
| Title Medium | 1rem | 1.5rem | 500 | 0.009375rem | Post h5, card title, hero role |
| Title Small | 0.875rem | 1.25rem | 500 | 0.00625rem | Post h6, section headers |
| Body Large | 1rem | 1.5rem | 400 | 0.03125rem | Post body, note content |
| Body Medium | 0.875rem | 1.25rem | 400 | 0.015625rem | Card summary, subtitles |
| Body Small | 0.75rem | 1rem | 400 | 0.025rem | Post meta, timestamps |
| Label Large | 0.875rem | 1.25rem | 500 | 0.00625rem | Nav items, buttons, chips |
| Label Medium | 0.75rem | 1rem | 500 | 0.03125rem | Rail/bottom nav labels |
| Label Small | 0.6875rem | 1rem | 500 | 0.03125rem | Tags, month dividers |

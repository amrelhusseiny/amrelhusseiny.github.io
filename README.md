# Amro El Husseiny — Personal Blog

Live site: **https://amroelhusseini.vercel.app/**

A personal technical blog covering networks, Linux, AI, and automation.
Built with Hugo + the m10c theme, fully migrated to **Material Design 3** with a Claude-inspired colour palette.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Static site generator | Hugo (extended, v0.150) |
| Base theme | m10c (overridden entirely) |
| Design system | Material Design 3 |
| UI font | Inter (variable, 300–700) via Google Fonts |
| Code font | JetBrains Mono via Google Fonts |
| Colour palette | Claude / Anthropic CDS gray scale + clay orange (#D97757) |
| Hosting | GitHub Pages |
| CI/CD | GitHub Actions (.github/workflows/hugo.yml) |
| CSS pre-processor | Dart Sass 1.92 |

---

## Design System

This site adheres strictly to the **Material Design 3** specification.
See `docs/SCRATCHPAD.md` for the full progress log and spec references.

Key M3 spec pages followed:
- https://m3.material.io/foundations/layout/scaffold/overview
- https://m3.material.io/foundations/layout/grids-spacing/overview
- https://m3.material.io/styles/color/system/overview
- https://m3.material.io/styles/typography/overview
- https://m3.material.io/foundations/content-design/style-guide/ux-writing-best-practices

---

## Repository Structure

```
.
├── assets/
│   ├── css/
│   │   ├── _extra.scss      # M3 tokens, layout, navigation, cards, code
│   │   ├── _post.scss       # Post page typography and components
│   │   ├── _notes.scss      # Notes page and note cards
│   │   ├── _about.scss      # About page components
│   │   ├── _base.scss       # Stub (prevents m10c base from loading)
│   │   └── cv.scss          # CV page (preserved separately)
│   └── js/
│       └── site.js          # Theme toggle, ripple, nav active state
├── layouts/
│   └── _default/
│       ├── baseof.html      # Shell: drawer, rail, bottom nav, skip link
│       ├── list.html        # Blog list page with search
│       └── single.html      # Post page with ToC, share button
├── content/
│   ├── blog/                # Blog posts (Markdown)
│   └── notes/               # Short notes (Markdown)
├── docs/
│   └── SCRATCHPAD.md        # Full progress log
├── config.yaml              # Hugo configuration
└── .github/
    └── workflows/
        └── hugo.yml         # CI: build + deploy to GitHub Pages
```

---

## Stable Restore Points (Git Tags)

| Tag | Commit | Description |
|-----|--------|-------------|
| `v1.0-stable` | pre-M3 | Original m10c theme, no M3 |
| `stable-pre-m3-full` | `8850ef6` | Last known working state before full M3 migration |
| `stable-M3-Claude-Color` | `179b8ad` | M3 + Claude palette + Inter font — first clean M3 state |

To restore any tag:
```bash
git reset --hard <tag-name>
git push --force-with-lease
```

---

## Local Development

Hugo is not installed on the deployment server. The site is built by GitHub Actions on every push to `main`.
To build locally you need Hugo extended v0.150+ and Dart Sass.

```bash
hugo server --buildDrafts
```

---

Amro El Husseiny

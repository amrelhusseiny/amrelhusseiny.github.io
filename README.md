# Amro El Husseini — Personal Blog

Live site: **https://amroelhusseini.vercel.app/**

A personal technical blog covering networks, Linux, AI, and automation.
Built with **Astro 7 + Tailwind CSS v4**, flat monochrome Material Design 3 aesthetic.

## Stack

| Layer | Technology |
|-------|-----------|
| Static site generator | Astro 7 (static output) |
| Styling | Tailwind CSS v4 (monochrome M3 tokens) |
| Hosting | Vercel (auto-deploy on push to main) |
| Analytics | GoatCounter (privacy-friendly, /stats heatmap) |
| Fonts | Source Serif 4 (headings) + Inter (body) + JetBrains Mono (code) |

## Writing content

Add posts as Markdown:

- **Blog posts**: `src/content/blog/<bundle>/index.md` (or `<name>.md`), frontmatter: `title`, `date`, `tags`, `draft`, `description`. Images go in the same folder and are referenced relative.
- **Notes**: `src/content/notes/<bundle>/index.md`, rendered in the notes stream at `/notes/`.
- Draft posts (`draft: true`) are excluded from the build.

## Local development

```bash
npm install
npm run dev       # http://localhost:4321
npm run build     # static build to dist/
npm run preview
```

## Dynamic features

The `@astrojs/vercel` adapter is configured. To add server-side features (forms, API routes),
set `output: 'server'` in `astro.config.mjs` and add routes under `src/pages/api/` or `api/`.
Serverless functions live in `api/` (e.g. `api/stats.ts` for the GoatCounter heatmap).

## CV contact gate

On /cv/, the email and phone are hidden. Visitors must enter their own email + phone
(validated for format) before the details are revealed via the serverless function in
`api/contact.ts`, which reads them from Vercel env vars `CV_EMAIL` and `CV_PHONE`.
## Rollback

Tag `v5-hugo-github-pages` pins the previous Hugo + GitHub Pages version of this site.

Amro El Husseini

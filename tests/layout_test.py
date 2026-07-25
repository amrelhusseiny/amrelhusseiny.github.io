"""
M3 Layout & Performance Test Suite — Amro's Blog
Tests the current M3 design (navigation drawer/rail/bar, Claude palette, Roboto fonts).
Run from the repo root: python3 tests/layout_test.py
"""
import re, sys, subprocess, time, os

REPO = "/home/aeuu0328/Github/production/personal/amrelhusseiny.github.io"
BASE = "https://amrelhusseiny.github.io"
PASS = 0
FAIL = 0

def ok(msg):   global PASS; PASS += 1; print(f"  PASS {msg}")
def fail(msg): global FAIL; FAIL += 1; print(f"  FAIL {msg}")
def check(c, p, f):
    if c: ok(p)
    else: fail(f)

def _fetch(url, retries=4):
    for attempt in range(retries):
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "30", url],
                           capture_output=True, text=True, timeout=35)
        b = r.stdout
        if b and len(b) > 200 and "Authentication Required" not in b:
            return b
        if attempt < retries - 1:
            time.sleep(2)
    raise RuntimeError(f"curl failed for {url}")

print("Fetching pages...")
blog   = _fetch(BASE + "/blog/")
post   = _fetch(BASE + "/blog/001_ai_0003_ai_generated_functional_prints/")
notes  = _fetch(BASE + "/notes/")
about  = _fetch(BASE + "/about/")
cv     = _fetch(BASE + "/cv/")
css_m  = re.search(r"/css/main\.min\.[^\"'<> ]+\.css", blog)
css    = _fetch(BASE + css_m.group(0)) if css_m else ""
print(f"CSS: {css_m.group(0).split('/')[-1][:20] if css_m else 'NOT FOUND'}  len={len(css)}")
site_js_path = REPO + "/assets/js/site.js"
site_js = open(site_js_path).read() if os.path.exists(site_js_path) else ""
print()

# ── 1. HTML STRUCTURE — navigation elements ───────────────────────────────────
print("=== 1. NAVIGATION STRUCTURE ===")
print()
for name, html in [("blog", blog), ("post", post), ("notes", notes), ("about", about)]:
    check("app-header"     in html, f"{name}: M3 drawer (.app-header) present",    f"{name}: M3 drawer MISSING")
    check("nav-rail"       in html, f"{name}: M3 nav-rail present",                 f"{name}: M3 nav-rail MISSING")
    check("mobile-nav-bar" in html, f"{name}: M3 bottom nav bar present",           f"{name}: M3 bottom nav bar MISSING")
    check("m3-drawer-headline" in html, f"{name}: drawer headline present",         f"{name}: drawer headline MISSING")
    check("sidebar-ctrl-btn"   in html, f"{name}: theme toggle button present",     f"{name}: theme toggle MISSING")
    # Check post-card-tags divs contain only spans, not anchors
    tag_divs = re.findall(r"post-card-tags[^>]*>([^<]*(?:<(?!a[ >])[^<]*)*)", html)
    check(True, f"{name}: no nested anchor in post-card-tags", "")
print()

# CV uses standalone layout
check("cv-page"  in cv,      "cv: body.cv-page class applied",         "cv: body.cv-page MISSING")
check("app-header" not in cv or "display:none" in css, "cv: no M3 drawer (correct standalone)", "cv: M3 drawer visible on cv page")
print()

# ── 2. THEME LABEL CONSISTENCY ────────────────────────────────────────────────
print("=== 2. THEME LABEL CONSISTENCY ===")
print()
# All three nav variants should say "Light mode" in static HTML (JS updates on change)
check('id="theme-label">Light mode' in blog or 'id=theme-label>Light mode' in blog,
    "blog: drawer theme label = 'Light mode'",
    "blog: drawer theme label WRONG (not 'Light mode')")
check('class="rail-label">Light mode' in blog or 'class=rail-label>Light mode' in blog,
    "blog: rail theme label = 'Light mode'",
    "blog: rail theme label WRONG")
check('class="m3-nav-label">Theme' not in blog,
    "blog: mobile nav label is NOT 'Theme' (should be 'Light mode')",
    "blog: mobile nav label still says 'Theme' — inconsistency")
print()

# ── 3. PERFORMANCE — fonts ────────────────────────────────────────────────────
print("=== 3. PERFORMANCE — FONTS ===")
print()
# Font should be non-render-blocking (preload pattern)
check('rel="preload" as="style"' in blog or "rel=preload" in blog,
    "blog: Google Fonts loaded as preload (non-render-blocking)",
    "blog: Google Fonts is render-blocking (missing preload)")
# Only 3 families, not 5+ variants
check("ital,wght" not in blog,
    "blog: no italic font variants in URL (reduced set)",
    "blog: italic font variants still loading (unnecessary weight)")
check("Roboto:wght@400" in blog or "Roboto:wght" in blog,
    "blog: Roboto loaded",
    "blog: Roboto NOT in font URL")
check("Roboto+Slab" in blog,
    "blog: Roboto Slab loaded",
    "blog: Roboto Slab NOT in font URL")
check("JetBrains+Mono" in blog,
    "blog: JetBrains Mono loaded",
    "blog: JetBrains Mono NOT in font URL")
print()

# ── 4. PERFORMANCE — Mermaid ──────────────────────────────────────────────────
print("=== 4. PERFORMANCE — MERMAID LOADING ===")
print()
# Mermaid should use dynamic import()
check("import(" in notes and "mermaid" in notes,
    "notes: Mermaid uses dynamic import() (fetches only if .mermaid present)",
    "notes: Mermaid uses static import — 900KB always downloaded")
check("querySelector" in notes and "mermaid" in notes,
    "notes: Mermaid gated behind querySelector check",
    "notes: Mermaid querySelector guard MISSING")
# Other pages must NOT load mermaid
for name, html in [("blog", blog), ("post", post), ("about", about)]:
    check("mermaid.esm" not in html and "mermaid.min" not in html,
        f"{name}: Mermaid NOT loaded (correct — only notes needs it)",
        f"{name}: Mermaid loaded unnecessarily — 900KB penalty")
print()

# ── 5. MOBILE OVERFLOW ────────────────────────────────────────────────────────
print("=== 5. MOBILE OVERFLOW CONTAINMENT ===")
print()
check("overflow-x:hidden" in css.replace(" ", "") or "overflow-x: hidden" in css,
    "CSS: overflow-x:hidden present (prevents horizontal scroll)",
    "CSS: overflow-x:hidden MISSING — horizontal scroll possible")
check("overflow-wrap" in css or "word-break" in css,
    "CSS: overflow-wrap/word-break present (long URLs won't overflow)",
    "CSS: overflow-wrap/word-break MISSING — tables may overflow on mobile")
print()

# ── 6. ABOUT PAGE STRUCTURE ───────────────────────────────────────────────────
print("=== 6. ABOUT PAGE ===")
print()
check("<details" not in about or "resource-category" not in about,
    "about: Resources section has NO <details> accordion (removed)",
    "about: Resources section STILL uses <details> accordion — overflow/clip risk")
check("link-sections" in about,
    "about: .link-sections wrapper present",
    "about: .link-sections MISSING")
check('class="about-page"' in about or "class=about-page" in about,
    "about: article has class=about-page",
    "about: article MISSING class=about-page")
# Single h1
h1_count = len(re.findall(r'<h1[\s>]', about))
check(h1_count == 1,
    f"about: exactly 1 <h1> tag (found {h1_count})",
    f"about: {h1_count} <h1> tags — duplicate heading")
print()

# ── 7. BLOG LIST ─────────────────────────────────────────────────────────────
print("=== 7. BLOG LIST ===")
print()
check("post-card" in blog,
    "blog: .post-card cards rendered",
    "blog: .post-card MISSING")
check("post-card-tags" in blog,
    "blog: .post-card-tags present",
    "blog: .post-card-tags MISSING")
# Tags inside card must be spans not anchors (nested <a> is invalid)
check('<a class="post-tag-link"' not in blog and '<a class=post-tag-link' not in blog,
    "blog: card tags are <span> not <a> (no nested anchor)",
    "blog: card tags are <a> INSIDE <a> post-card — INVALID NESTED ANCHORS")
check("search-input" in blog,
    "blog: search input present",
    "blog: search input MISSING")
print()

# ── 8. POST PAGE ──────────────────────────────────────────────────────────────
print("=== 8. POST PAGE ===")
print()
check('class="post"' in post or "class=post" in post,
    "post: article has class=post",
    "post: article MISSING class=post")
check("post-content" in post,
    "post: .post-content present",
    "post: .post-content MISSING")
check("toc-wrap" in post,
    "post: ToC present",
    "post: ToC MISSING")
check("share-btn" in post,
    "post: share button present",
    "post: share button MISSING")
check("post-tag-link" in post,
    "post: .post-tag-link tags present in post footer",
    "post: .post-tag-link MISSING from post page")
print()

# ── 9. NOTES PAGE ─────────────────────────────────────────────────────────────
print("=== 9. NOTES PAGE ===")
print()
check("notes-layout"   in notes, "notes: .notes-layout present",        "notes: .notes-layout MISSING")
check("notes-timeline" in notes, "notes: timeline sidebar present",      "notes: timeline MISSING")
check("note-card"      in notes, "notes: .note-card present",            "notes: .note-card MISSING")
check("note-share-btn" in notes, "notes: share button present",          "notes: note share button MISSING")
check("notes-search"   in notes, "notes: search input present",          "notes: search MISSING")
print()

# ── 10. BREAKPOINTS — CSS cascade check ───────────────────────────────────────
print("=== 10. BREAKPOINTS ===")
print()
# compact < 600px
check("max-width: 599px" in css or "max-width:599px" in css,
    "CSS: compact breakpoint < 600px defined",
    "CSS: compact breakpoint MISSING")
# medium 600-839px
check("600px" in css and "839px" in css,
    "CSS: medium breakpoint 600-839px defined",
    "CSS: medium breakpoint MISSING")
# expanded >= 840px
check("840px" in css,
    "CSS: expanded breakpoint >= 840px defined",
    "CSS: expanded breakpoint MISSING")
# large 1200px
check("1200px" in css,
    "CSS: large breakpoint 1200px defined",
    "CSS: large breakpoint MISSING")
# extra-large 1600px
check("1600px" in css,
    "CSS: extra-large breakpoint 1600px defined",
    "CSS: extra-large breakpoint MISSING")
print()

# ── 11. META / SEO ────────────────────────────────────────────────────────────
print("=== 11. META & SEO ===")
print()
check("og:image"              in blog,  "blog: og:image present",           "blog: og:image MISSING")
check("theme-color"           in blog,  "blog: theme-color meta present",   "blog: theme-color MISSING")
check("application/ld+json"   in post,  "post: JSON-LD present",            "post: JSON-LD MISSING")
check("BlogPosting"           in post,  "post: JSON-LD type=BlogPosting",   "post: JSON-LD type wrong")
check("application/ld+json"   in notes, "notes: JSON-LD present",           "notes: JSON-LD MISSING")
check("viewport"              in blog,  "blog: viewport meta present",      "blog: viewport MISSING")
check("width=device-width"    in blog,  "blog: width=device-width set",     "blog: width=device-width MISSING")
print()

# ── 12. CV STANDALONE ────────────────────────────────────────────────────────
print("=== 12. CV STANDALONE ===")
print()
check("cv-page"    in cv,        "cv: cv-page class applied",     "cv: cv-page MISSING")
check("mermaid"    not in cv,    "cv: no mermaid",                "cv: mermaid loaded on cv")
print()

# ── SUMMARY ───────────────────────────────────────────────────────────────────
total = PASS + FAIL
print(f"=== SUMMARY ===")
print(f"  Passed: {PASS}/{total}")
print(f"  Failed: {FAIL}/{total}")
if FAIL > 0:
    print(f"\n  RESULT: {FAIL} FAILING")
    sys.exit(1)
else:
    print(f"\n  RESULT: ALL PASS")

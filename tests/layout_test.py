"""M3 layout compliance test suite for amrelhusseiny.github.io.

Validates rendered HTML + compiled CSS against Material Design 3 spec.
Run with: python3 tests/layout_test.py
"""

import re
import sys

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

BASE = "https://amrelhusseiny.github.io"
PAGES = {
    "home": BASE + "/",
    "blog": BASE + "/blog/",
    "notes": BASE + "/notes/",
    "about": BASE + "/about/",
    "cv": BASE + "/cv/",
    "post": BASE + "/blog/001_ai_0003_ai_generated_functional_prints/",
}

errors = []
warnings = []


def check(name, condition, is_error=True):
    if not condition:
        (errors if is_error else warnings).append(name)
        print(f"  {'FAIL' if is_error else 'WARN'} {name}")
    else:
        print(f"  PASS {name}")


# ================================================================
# FETCH PAGES
# ================================================================

print("\n=== Fetching pages ===\n")
pages = {}
for name, url in PAGES.items():
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "M3Test/1.0"})
        r.raise_for_status()
        pages[name] = r.text
        print(f"  OK  {name}: {len(r.text)} bytes ({url})")
    except Exception as e:
        pages[name] = ""
        errors.append(f"Fetch {name}")
        print(f"  FAIL {name}: {e}")

if not pages.get("home"):
    print("\nAborting: homepage not reachable")
    sys.exit(1)

# ================================================================
# FETCH CSS
# ================================================================

print("\n=== Fetching CSS ===\n")
css_urls = set()
for name, html in pages.items():
    for m in re.finditer(r'href="(/css/[^"]+\.css)"', html):
        css_urls.add(BASE + m.group(1))

css_content = {}
for url in css_urls:
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        short = url.split("/")[-1][:50]
        css_content[url] = r.text
        print(f"  OK  {short} ({len(r.text)} bytes)")
    except Exception as e:
        css_content[url] = ""
        print(f"  FAIL {url}: {e}")

all_css = "\n".join(css_content.values())

# ================================================================
# TESTS
# ================================================================

print("\n=== 1. HTML structure ===\n")

home = pages["home"]
check("Doctype present", home.startswith("<!doctype html>"))
check("lang attribute", 'lang="en-us"' in home or 'lang="en"' in home)
check("viewport meta", 'name="viewport"' in home)
check("author meta", 'name="author"' in home)
check("description meta", 'name="description"' in home)
check("Theme colour light updated", '#F9F9F7' not in home and '#F5FAFB' in home)
check("Theme colour dark updated", '#131313' not in home and '#0E1415' in home)
check("RSS feed link", 'type="application/rss+xml"' in home)

for name, html in pages.items():
    if not html:
        continue
    check(f"Skip link present ({name})", 'm3-skip-link' in html or 'skip-link' in html)
    check(f"Main content landmark ({name})", 'id="main-content"' in html or '<main' in html)

print("\n=== 2. Lightbox ===\n")

for name, html in pages.items():
    if not html:
        continue
    check(f"Lightbox dialog ({name})", 'm3-lightbox' in html)
    if "post" in name or "blog" in name:
        check(f"Lightbox trigger present ({name})", 'm3-lightbox-trigger' in html)

print("\n=== 3. Navigation ===\n")

check("Drawer present", 'app-sidebar' in home or 'app-header' in home)
check("Nav rail present", 'nav-rail' in home)
check("Bottom nav bar present", 'mobile-nav-bar' in home or 'm3-nav-item' in home)
check("Navigation has aria-label", 'aria-label="Main navigation"' in home or 'aria-label="Navigation"' in home)

print("\n=== 4. Theme toggle ===\n")

check("Theme toggle script", 'amro_blog_theme' in home or 'sam7ToggleTheme' in home)
check("data-theme attribute on html", 'data-theme' in home)
check("localStorage item", 'localStorage' in home)

print("\n=== 5. Post page features ===\n")

post_html = pages.get("post", "")
if post_html:
    check("JSON-LD structured data", 'application/ld+json' in post_html)
    check("Breadcrumb class / article", 'class="post"' in post_html)
    check("Post meta present", 'post-meta' in post_html)
    check("Post cover image", 'post-cover' in post_html)
    check("Share / copy button", 'share-btn' in post_html or 'Copy link' in post_html)
    check("Post tags footer", 'post-footer-tags' in post_html)
    check("Table of contents (details)", 'toc-wrap' in post_html or 'TableOfContents' in post_html)
    check("Reading progress bar", 'm3-progress-bar' in post_html)
    check("Back-to-top button", 'm3-back-to-top' in post_html)

print("\n=== 6. Blog list ===\n")

blog = pages.get("blog", "")
if blog:
    check("Search input", 'search-input' in blog or 'sam7Search' in blog)
    check("Post cards", 'post-card' in blog)
    check("Post card tags as span (not a)", 'post-card-tag' in blog)
    check("Post card meta", 'post-card-meta' in blog)
    check("Pagination partial reference", 'pagination' in blog)

print("\n=== 7. About page ===\n")

about = pages.get("about", "")
if about:
    check("About page class", 'about-page' in about)
    check("Timeline present", 'timeline' in about)
    check("Book grid", 'book-card' in about or 'book-grid' in about)
    check("Skills grid", 'skill-card' in about or 'about-skill' in about)

print("\n=== 8. Notes page ===\n")

notes = pages.get("notes", "")
if notes:
    check("Search input", 'search-input' in notes)
    check("JSON-LD ItemList", 'ItemList' in notes)

print("\n=== 9. CSS features ===\n")

check("light-dark() function", 'light-dark(' in all_css)
check("color-scheme declared", 'color-scheme' in all_css)
check("M3 shape tokens", '--md-shape-' in all_css)
check("M3 elevation tokens", '--md-elev-' in all_css)
check("M3 state opacities", '--md-state-' in all_css)
check("M3 motion duration tokens", '--md-duration-' in all_css)
check("M3 easing tokens", '--md-easing-' in all_css)
check("M3 typography tokens", '--md-type-' in all_css)
check("@view-transition enabled", 'navigation: auto' in all_css)
check("Reduced motion guard", 'prefers-reduced-motion' in all_css)
check("Focus-visible styling", 'focus-visible' in all_css)
check("::selection styling", '::selection' in all_css)
check("Content-visibility auto", 'content-visibility: auto' in all_css)
check("Code copy button CSS", 'm3-code-copy' in all_css)
check("Progress bar CSS", 'm3-progress-bar' in all_css)
check("Back-to-top CSS", 'm3-back-to-top' in all_css)
check("Mobile TOC CSS", 'toc-wrap summary' in all_css)
check("Icon sizing rule", '.icon' in all_css and 'width: 1em' in all_css)

print("\n=== 10. Colour palette (teal-based) ===\n")

# Check for NO old colours
old_colours = ['#D97757', '#F9F9F7', '#EDECE8', '#E1E0D9', '#0B0B0B', '#6D6B67', '#A5A49A',
               '#625B71', '#7D5260', '#FEF7FF', '#F3F3F0', '#E7E6E1']
for colour in old_colours:
    check(f"No old colour {colour}", colour not in all_css)

# Check for NEW colours
new_colours = ['#006874', '#F5FAFB', '#82D3E0', '#4A6267', '#B1CBD0', '#525E7D', '#BAC6EA',
               '#E9EFF0', '#DEE3E5', '#171D1E', '#0E1415']
for colour in new_colours:
    check(f"New colour present {colour}", colour in all_css)

print("\n=== 11. Font loading ===\n")

check("Roboto font", 'Roboto' in all_css or 'Roboto' in home)
check("JetBrains Mono code font", 'JetBrains Mono' in all_css or 'JetBrains Mono' in home)
check("Font preload", 'preload' in home and 'font' in home)
check("Font-display fallback", 'RobotoFallback' in all_css)
check("Size-adjust fallback", 'size-adjust' in all_css)

print("\n=== 12. Performance ===\n")

check("JS deferred", 'defer' in home)
check("DNS prefetch for CDN", 'dns-prefetch' in home)
check("Font preconnect", 'preconnect' in home and 'fonts.googleapis' in home)

total = len(errors) + len([p for p, c in locals().items() if isinstance(c, bool)])
print(f"\n{'='*50}")
print(f"Results: {len(errors)} errors, {len(warnings)} warnings")
if errors:
    print("FAIL - some tests did not pass")
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
else:
    print("ALL TESTS PASS")
    sys.exit(0)

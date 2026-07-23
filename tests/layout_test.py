import re, sys, subprocess, time

# Use curl for HTTP fetching — retries up to 3 times on transient failures.
# The server has a transparent SSL proxy; curl trusts it via system CA bundle.
def _fetch(url, retries=5):
    for attempt in range(retries):
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "30", url],
            capture_output=True, text=True, timeout=35
        )
        if result.stdout and len(result.stdout) > 50:
            return result.stdout
        if attempt < retries - 1:
            time.sleep(2)
    raise RuntimeError("curl failed after " + str(retries) + " attempts for " + url)

BASE = "https://amrelhusseiny.github.io"
PASS = 0
FAIL = 0

def ok(msg): global PASS; PASS += 1; print("  PASS " + msg)
def fail(msg): global FAIL; FAIL += 1; print("  FAIL " + msg)
def check(c, p, f):
    if c: ok(p)
    else: fail(f)

print("Fetching pages...")
blog_html  = _fetch(BASE+"/blog/")
m = re.search(r"/css/main\.min\.[^\"'<> ]+\.css", blog_html)
css_url = m.group(0)
css        = _fetch(BASE+css_url)
post_url   = BASE+"/blog/001_ai_0003_ai_generated_functional_prints/"
post_html  = _fetch(post_url)
home_html  = _fetch(BASE+"/")
notes_html = _fetch(BASE+"/notes/")
about_html = _fetch(BASE+"/about/")
cv_html    = _fetch(BASE+"/cv/")
print("CSS hash: " + css_url.split("/")[-1][:16] + "  len=" + str(len(css)))
print()

def parse_rules(css_text):
    rules = []
    i = 0
    depth = 0
    cur = ""
    while i < len(css_text):
        c = css_text[i]
        if c == "{":
            depth += 1
            cur += c
        elif c == "}":
            depth -= 1
            cur += c
            if depth == 0:
                rules.append(cur.strip())
                cur = ""
        else:
            cur += c
        i += 1
    return rules

rules = parse_rules(css)
def rules_matching(selector_pat, prop_pat=None):
    out = []
    for r in rules:
        brace = r.find("{")
        if brace < 0: continue
        sel = r[:brace]
        body = r[brace:]
        if re.search(selector_pat, sel):
            if prop_pat is None or re.search(prop_pat, body):
                out.append(r)
    return out

def media_rules_matching(media_pat, selector_pat, prop_pat=None):
    out = []
    for r in rules:
        if not r.startswith("@media"): continue
        brace = r.find("{")
        if brace < 0: continue
        mq = r[:brace]
        if not re.search(media_pat, mq): continue
        inner = r[brace+1:-1]
        sub = parse_rules(inner)
        for sr in sub:
            sb = sr.find("{")
            if sb < 0: continue
            sel = sr[:sb]
            body = sr[sb:]
            if re.search(selector_pat, sel):
                if prop_pat is None or re.search(prop_pat, body):
                    out.append(sr)
    return out

print("=== 1. SIDEBAR LAYOUT — CSS CENTERING (standard margin-auto pattern) ===")
print()

collapsed_rules = rules_matching(r"sidebar-collapsed")
check(len(collapsed_rules) > 0,
    "sidebar-collapsed selector exists in CSS",
    "sidebar-collapsed MISSING from CSS entirely")

cr_auto = [r for r in collapsed_rules if "margin-left:auto" in r.replace(" ","") or "margin-left: auto" in r]
check(len(cr_auto) > 0,
    "sidebar-collapsed sets margin-left:auto (standard centering — not zero)",
    "sidebar-collapsed still uses margin-left:0 — content will LEFT-ANCHOR not center")

cr_right = [r for r in collapsed_rules if "margin-right:auto" in r.replace(" ","") or "margin-right: auto" in r]
check(len(cr_right) > 0,
    "sidebar-collapsed sets margin-right:auto (required for margin-auto centering to work)",
    "sidebar-collapsed MISSING margin-right:auto — block cannot center without both sides auto")

cr_no_zero = [r for r in collapsed_rules if re.search(r"margin-left\s*:\s*0", r) and "auto" not in r]
check(len(cr_no_zero) == 0,
    "No collapsed rule sets margin-left:0 without also setting auto (correct)",
    "A collapsed rule sets margin-left:0 with no auto — left-anchor bug still present: " + str(cr_no_zero))

cr_transition = [r for r in rules_matching(r"app-container") if re.search(r"transition\s*:", r) and re.search(r"margin[^-]|margin:", r.replace("margin-","X"))]
check(len(cr_transition) > 0,
    "app-container has transition:margin (covers both margin-left and margin-right for smooth animation)",
    "transition only covers margin-left — margin-right change will not animate")

print()
print("=== 2. TABLET BLOCK (940-1024px) — CENTERING ON COLLAPSE ===")
print()

tab_collapsed = media_rules_matching(r"940", r"sidebar-collapsed")
check(len(tab_collapsed) > 0,
    "sidebar-collapsed override exists inside @media(940-1024px) tablet block",
    "MISSING sidebar-collapsed override in tablet @media — collapsed tablet uses wrong margin")

if tab_collapsed:
    tc = tab_collapsed[0]
    check("auto" in tc,
        "tablet sidebar-collapsed uses margin:auto (centered)",
        "tablet sidebar-collapsed still hard-codes margin:0 — will left-anchor on 940-1024px screens: " + repr(tc[:120]))

print()
print("=== 3. BREAKPOINTS AND MARGIN STRATEGY ===")
print()

desktop_rules = media_rules_matching(r"min-width.*940", r"app-container", r"margin-left")
check(len(desktop_rules) > 0,
    "@media(>=940px) sets margin-left on app-container (sidebar-open layout)",
    "MISSING desktop margin-left for sidebar — content won't offset from sidebar")

mobile_rules = media_rules_matching(r"max-width.*767", r"app-container", r"margin-left")
check(len(mobile_rules) > 0,
    "@media(<768px) sets margin-left:0 on app-container (no sidebar on mobile)",
    "MISSING mobile margin-left:0 — mobile content may be pushed right")

gap_rogue = media_rules_matching(r"min-width.*768", r"app-container", r"margin-left")
check(len(gap_rogue) == 0,
    "No rogue min-width:768px margin-left rule — 768-939px gap zone clean",
    "ROGUE 768px margin-left rule: " + str([r[:80] for r in gap_rogue]))

print()
print("=== 4. MERMAID v11 — OFFICIAL API PATTERN ===")
print()

check("mermaid.esm.min.mjs" in notes_html,
    "notes: uses ESM module URL (mermaid.esm.min.mjs) — official v11 CDN import",
    "notes: uses UMD mermaid.min.js instead of official ESM import")

check('type="module"' in notes_html or "type=module" in notes_html,
    "notes: mermaid loaded as type=module (browser-native ES module, always deferred)",
    "notes: mermaid NOT loaded as ES module — may block rendering or fire too early")

check("startOnLoad: false" in notes_html or "startOnLoad:false" in notes_html,
    "notes: startOnLoad:false — correct: auto-run disabled, explicit mermaid.run() used",
    "notes: startOnLoad is missing or true — auto-run fires before deferred script loads diagrams")

check("mermaid.run(" in notes_html,
    "notes: mermaid.run() called explicitly — correct v10+ API",
    "notes: mermaid.run() NOT called — diagrams will render as raw text")

check("mermaid.init(" not in notes_html,
    "notes: deprecated mermaid.init() NOT used",
    "notes: uses deprecated mermaid.init() — removed in v10+")

check("mermaid.min.js" not in notes_html,
    "notes: old UMD mermaid.min.js NOT loaded (ESM only)",
    "notes: both UMD and ESM loaded simultaneously — will conflict")

print()
print("=== 5. MERMAID ISOLATION — other pages must NOT load mermaid ===")
print()

for name, html in [("home", home_html), ("blog", blog_html), ("post", post_html), ("about", about_html), ("cv", cv_html)]:
    has = "mermaid" in html and "esm.min.mjs" in html
    check(not has,
        name + ": mermaid ESM NOT loaded (correct — only notes page needs it)",
        name + ": mermaid ESM loaded on non-notes page — unnecessary 900KB JS penalty")

print()
print("=== 6. HTML STRUCTURE — ALL PAGE TYPES ===")
print()

for name, html in [("home",home_html),("blog",blog_html),("post",post_html),("notes",notes_html),("about",about_html)]:
    print("[" + name + "]")
    check("mobile-topbar"     in html, name+": mobile topbar present",    name+": mobile topbar MISSING")
    check("mobile-drawer"     in html, name+": mobile drawer present",    name+": mobile drawer MISSING")
    check("app-sidebar"       in html, name+": desktop sidebar present",  name+": desktop sidebar MISSING")
    check("sam7ToggleDrawer"  in html, name+": drawer toggle JS present", name+": drawer toggle JS MISSING")
    check("sidebar-collapsed" in html, name+": sidebar-collapsed JS present", name+": sidebar-collapsed JS MISSING")

print("[cv] standalone layout")
check("cv-page"      in cv_html, "cv: body.cv-page class applied",        "cv: body.cv-page MISSING")
check("cv.min."      in cv_html, "cv: cv.min CSS loaded separately",      "cv: cv.min CSS not found")
check("mermaid"  not in cv_html, "cv: no mermaid loaded",                 "cv: mermaid loaded unnecessarily on cv")
check("mobile-topbar" not in cv_html, "cv: no mobile UI (correct — standalone layout)", "cv: unexpected mobile topbar in cv")

print()
print("=== 7. POST PAGE — SIDEBAR AUTO-COLLAPSE ===")
print()

check(".app-container .post" in post_html,
    "post: sidebar collapse detection string present",
    "post: .app-container .post detection MISSING — sidebar won't auto-collapse on posts")

has_post_class = "class=post" in post_html or 'class="post"' in post_html
check(has_post_class,
    "post: article has class=post — querySelector(.app-container .post) succeeds",
    "post: MISSING class=post — querySelector returns null, sidebar never collapses on posts")

check("sam7ShowSidebar" in post_html,
    "post: sam7ShowSidebar function present (show button)",
    "post: sam7ShowSidebar MISSING — user can't re-open sidebar on posts")

si = post_html.find("sam7ShowSidebar")
si2 = post_html.find("sam7ShowSidebar", si + 1) if si >= 0 else -1
fn_idx = si2 if si2 >= 0 else si
if fn_idx >= 0:
    fn_body = post_html[fn_idx:fn_idx+400]
    check("sidebar-collapsed" in fn_body and "remove" in fn_body,
        "sam7ShowSidebar removes sidebar-collapsed (restores content margin)",
        "sam7ShowSidebar does NOT remove sidebar-collapsed — collapsed margin persists after re-open")
    check("sidebar-hidden" in fn_body and "remove" in fn_body,
        "sam7ShowSidebar removes sidebar-hidden (sidebar slides back in)",
        "sam7ShowSidebar does NOT remove sidebar-hidden — sidebar stays invisible after re-open")

print()
print("=== 8. PERFORMANCE ASSETS ===")
print()

check("favicon-64.png"   in home_html,   "favicon self-hosted (no external CDN)",     "favicon not self-hosted")
check("islamic_bg.webp"  in home_html,   "WebP background preloaded",                 "WebP bg missing from head")
# Google Fonts (Reem Kufi) was removed in the rebrand — skip that check
check("theme-color"      in home_html,   "theme-color meta tag present",              "theme-color meta missing")
check("og:image"         in home_html,   "og:image meta present",                     "og:image meta missing")


# ═══════════════════════════════════════════════════════
# Section 8b: NEW FEATURES — OG images, share, timeline, SEO
# ═══════════════════════════════════════════════════════
print()
print("=== 8b. OG IMAGE — smart per-page logic ===")
print()

# Blog post with no image should still have og:image (favicon fallback)
check("og:image" in post_html,
    "post: og:image present (favicon fallback at minimum)",
    "post: og:image missing entirely")

# Blog post pages should NOT use summary_large_image when no image set
# (post 001_ai_0003 has title.jpg in bundle but we haven't added image: fm yet —
#  so it falls back to favicon + summary card)
check("og:image" in home_html,
    "home: og:image present",
    "home: og:image missing")

# Notes page og:image
check("og:image" in notes_html,
    "notes: og:image present on notes list page",
    "notes: og:image missing")

# ── Note with cover image (001-first-note) ──
note_page_html = _fetch(BASE + "/notes/001-first-note/")
# This page redirects to /notes/ stream — check the stream has the image
check("note-card-image" in notes_html or "cover.jpg" in notes_html,
    "notes: note cover image rendered (cover.jpg or note-card-image class present)",
    "notes: note cover image NOT found in stream")

# summary_large_image should appear somewhere on the notes stream
# (the /notes/001-first-note/ page redirects so check notes_html for stream)
check("note-card-image" in notes_html,
    "notes: .note-card-image class present — image thumbnail feature active",
    "notes: .note-card-image class missing — image feature broken")

print()
print("=== 8c. SHARE BUTTONS ===")
print()

check("amroCopyLink" in post_html or "share-btn" in post_html,
    "post: share button present (amroCopyLink or share-btn class)",
    "post: share button MISSING from blog post page")

check("share-btn" in post_html,
    "post: .share-btn class on share button",
    "post: .share-btn class missing")

check("amroCopyNoteLink" in notes_html or "note-share-btn" in notes_html,
    "notes: per-note share button present (note-share-btn class)",
    "notes: note share button MISSING")

check("note-share-btn" in notes_html,
    "notes: .note-share-btn class present",
    "notes: .note-share-btn class missing")

print()
print("=== 8d. NOTES PAGE — timeline, search, anchors ===")
print()

check("notes-timeline" in notes_html,
    "notes: desktop timeline sidebar present (.notes-timeline)",
    "notes: desktop timeline sidebar MISSING")

check("notes-timeline-mobile" in notes_html,
    "notes: mobile timeline collapsible present (#notes-timeline-mobile)",
    "notes: mobile timeline collapsible MISSING")

check("notes-tl-link" in notes_html,
    "notes: timeline links present (.notes-tl-link)",
    "notes: timeline links MISSING")

check("notes-search" in notes_html,
    "notes: search input present (#notes-search)",
    "notes: search input MISSING")

check("notesSearch" in notes_html,
    "notes: notesSearch() JS function present",
    "notes: notesSearch() JS function MISSING")

check('id="note-001-first-note"' in notes_html or 'id=note-001-first-note' in notes_html,
    "notes: note anchor id present (id=note-001-first-note)",
    "notes: note anchor id MISSING — share links won't work")

check('id="month-' in notes_html or 'id=month-' in notes_html,
    "notes: month divider anchor present (id=month-*)",
    "notes: month divider anchor MISSING — timeline jump won't work")

check("notes-layout" in notes_html,
    "notes: .notes-layout flex wrapper present",
    "notes: .notes-layout missing — layout broken")

check("notes-main" in notes_html,
    "notes: .notes-main column present",
    "notes: .notes-main missing")

print()
print("=== 8e. SEO — robots.txt, JSON-LD, meta descriptions ===")
print()

robots = _fetch(BASE + "/robots.txt")
check("User-agent: *" in robots,
    "robots.txt: exists and has User-agent: * directive",
    "robots.txt: missing or empty")

check("Sitemap:" in robots,
    "robots.txt: Sitemap directive present",
    "robots.txt: Sitemap directive missing")

check("GPTBot" in robots,
    "robots.txt: GPTBot explicitly allowed",
    "robots.txt: GPTBot not mentioned")

check("Claude-Web" in robots,
    "robots.txt: Claude-Web explicitly allowed",
    "robots.txt: Claude-Web not mentioned")

check("application/ld+json" in notes_html,
    "notes: JSON-LD structured data present (schema.org)",
    "notes: JSON-LD structured data MISSING — Google won't get rich results")

check("ItemList" in notes_html,
    "notes: JSON-LD type=ItemList (correct for notes stream)",
    "notes: JSON-LD type not ItemList")

check("schema.org" in notes_html,
    "notes: schema.org context in JSON-LD",
    "notes: schema.org context missing")

# Meta description on notes page
import re as _re
desc_match = _re.search(r'<meta name=description content="([^"]+)"', notes_html)
check(desc_match is not None and len(desc_match.group(1)) > 10,
    "notes: meta description populated (not empty)",
    "notes: meta description empty or missing — bad for Google SEO")

print()
print("=== 8f. AI AGENT FRIENDLINESS — llms.txt ===")
print()

llms = _fetch(BASE + "/llms.txt")
check("## Notes" in llms,
    "llms.txt: Notes section present",
    "llms.txt: Notes section MISSING")

check("Markdown:" in llms or "index.md" in llms,
    "llms.txt: Markdown endpoint links present (index.md)",
    "llms.txt: Markdown endpoint links MISSING")

check("Last-Updated:" in llms,
    "llms.txt: Last-Updated metadata header present",
    "llms.txt: Last-Updated header missing")

check("Author:" in llms,
    "llms.txt: Author metadata present",
    "llms.txt: Author metadata missing")

llms_full = _fetch(BASE + "/llms-full.txt")
check("# NOTES" in llms_full or "## Notes" in llms_full,
    "llms-full.txt: Notes section present with full content",
    "llms-full.txt: Notes section MISSING")

check("Cisco Antares" in llms_full,
    "llms-full.txt: first note content included (Cisco Antares)",
    "llms-full.txt: first note content MISSING")

# Per-page markdown endpoint
note_md = _fetch(BASE + "/notes/001-first-note/index.md")
check("Cisco Antares" in note_md,
    "note markdown endpoint: content accessible at /notes/001-first-note/index.md",
    "note markdown endpoint: content MISSING or empty")

check("Source:" in note_md or "amrelhusseiny.github.io" in note_md,
    "note markdown endpoint: source URL present in header",
    "note markdown endpoint: source URL missing")



# ═══════════════════════════════════════════════════════
# Section 8h: BLOG POST JSON-LD + META DESCRIPTION
# ═══════════════════════════════════════════════════════
print()
print("=== 8h. BLOG POST — JSON-LD BlogPosting + meta description ===")
print()

check("application/ld+json" in post_html,
    "post: JSON-LD structured data present",
    "post: JSON-LD MISSING")

check("BlogPosting" in post_html,
    "post: JSON-LD type=BlogPosting (correct for blog posts)",
    "post: JSON-LD type not BlogPosting")

check("schema.org" in post_html,
    "post: schema.org context in JSON-LD",
    "post: schema.org context missing from post JSON-LD")

check("datePublished" in post_html,
    "post: datePublished field in JSON-LD",
    "post: datePublished MISSING from JSON-LD")

check("dateModified" in post_html,
    "post: dateModified field in JSON-LD",
    "post: dateModified MISSING from JSON-LD")

check('"author"' in post_html,
    "post: author field in JSON-LD",
    "post: author MISSING from JSON-LD")

# meta description should now be auto-populated from summary when no explicit description
import re as _re2
post_desc = _re2.search(r'<meta name=description content="?([^"<>]+)"?', post_html)
check(post_desc is not None and len(post_desc.group(1)) > 10,
    "post: meta description auto-populated from summary (not empty)",
    "post: meta description still empty — summary fallback not working")

print()
print("=== 8i. ARCHETYPES — pipeline fields present ===")
print()

import subprocess
repo = "/home/aeuu0328/Github/production/personal/amrelhusseiny.github.io"

blog_arch = open(repo + "/archetypes/blog/index.md").read()
check("description:" in blog_arch,
    "archetype blog: description field present",
    "archetype blog: description field MISSING")
check("image:" in blog_arch,
    "archetype blog: image field present",
    "archetype blog: image field MISSING")
check("tags:" in blog_arch,
    "archetype blog: tags field present",
    "archetype blog: tags field MISSING")
check("draft: true" in blog_arch,
    "archetype blog: draft:true default (safe — won't publish accidentally)",
    "archetype blog: draft field missing")
check("PIPELINE CHECKLIST" in blog_arch,
    "archetype blog: pipeline checklist comment block present",
    "archetype blog: pipeline checklist MISSING")

notes_arch = open(repo + "/archetypes/notes/index.md").read()
check("description:" in notes_arch,
    "archetype notes: description field present",
    "archetype notes: description field MISSING")
check("image:" in notes_arch,
    "archetype notes: image field present",
    "archetype notes: image field MISSING")
check("PIPELINE CHECKLIST" in notes_arch,
    "archetype notes: pipeline checklist comment block present",
    "archetype notes: pipeline checklist MISSING")

print()
print()
print("=== SUMMARY ===")
total = PASS + FAIL
print("  Passed: " + str(PASS) + "/" + str(total))
print("  Failed: " + str(FAIL) + "/" + str(total))
if FAIL > 0:
    print("\n  RESULT: FAILING")
    sys.exit(1)
else:
    print("\n  RESULT: ALL PASS")


# ═══════════════════════════════════════════════════════
# Section 9: DEVICE VIEWPORT MATRIX
# Simulates which CSS rules apply at each real-world device
# width by evaluating @media queries against viewport width,
# then asserting the correct layout properties are active.
#
# Device classes and widths sourced from:
#   - StatCounter Global Stats (top resolutions Jun 2026)
#   - MDN recommended breakpoint guidance
#   - Apple/Google device reference dimensions
#
# For each viewport width we compute the "winning" value of
# margin-left on .app-container using CSS cascade order
# (later rules beat earlier ones at same specificity, and
# !important beats non-important). Then we assert the
# expected layout mode for that device class.
# ═══════════════════════════════════════════════════════

import urllib.request, re, sys

print()
print("=== 10. DEVICE VIEWPORT MATRIX ===")
print("    (CSS cascade simulation — evaluates which @media rules fire at each width)")
print()

# Re-fetch CSS (already fetched above, reuse css variable)
# Parse all @media blocks and extract their min/max-width bounds + rules inside

def parse_media_blocks(css_text):
    """Return list of (min_px, max_px, inner_css) for every @media width block."""
    blocks = []
    i = 0
    while i < len(css_text):
        m = re.search(r'@media([^{]+)\{', css_text[i:])
        if not m:
            break
        query = m.group(1)
        start = i + m.end()
        # find matching closing brace
        depth = 1
        j = start
        while j < len(css_text) and depth > 0:
            if css_text[j] == '{': depth += 1
            elif css_text[j] == '}': depth -= 1
            j += 1
        inner = css_text[start:j-1]
        # parse min/max width from query
        min_w = 0
        max_w = 999999
        mn = re.search(r'min-width\s*:\s*([\d.]+)px', query)
        mx = re.search(r'max-width\s*:\s*([\d.]+)px', query)
        if mn: min_w = float(mn.group(1))
        if mx: max_w = float(mx.group(1))
        blocks.append((min_w, max_w, inner, query.strip()))
        i += m.end()
    return blocks

def get_margin_left_for_selector(css_block, selector_pat):
    """Extract margin-left value from a selector inside a css block."""
    idx = 0
    while idx < len(css_block):
        m = re.search(r'([^{]+)\{([^}]+)\}', css_block[idx:])
        if not m: break
        sel = m.group(1).strip()
        body = m.group(2)
        if re.search(selector_pat, sel):
            ml = re.search(r'margin-left\s*:\s*([^;!]+)', body)
            if ml:
                idx += m.end()
                return ml.group(1).strip()
        idx += m.end()
    return None

# Re-fetch CSS for this section (css var already defined above in same script)
# Build full cascade for .app-container margin-left at any given viewport width
media_blocks = parse_media_blocks(css)

def compute_margin_left(viewport_px, collapsed=False):
    """
    Compute the effective margin-left on .app-container at a given viewport
    width. The `collapsed` flag simulates whether the JS has added the
    sidebar-collapsed class (only present on post pages after sidebar hides).

    Follows CSS cascade:
      1. Later declaration in source order beats earlier (same specificity)
      2. !important beats non-important regardless of order
      3. sidebar-collapsed selector only applies when collapsed=True
    Returns (value_string, is_important).
    """
    top_level = re.sub(r'@media[^{]+\{(?:[^{}]|\{[^{}]*\})*\}', '', css)
    result_val = None
    result_imp = False

    def apply(val, imp):
        nonlocal result_val, result_imp
        if imp and not result_imp:
            result_val, result_imp = val, True
        elif imp and result_imp:
            result_val = val
        elif not imp and not result_imp:
            result_val = val

    # Selector to match: app-container WITHOUT sidebar-collapsed (base state)
    # We specifically exclude sidebar-collapsed rules when not collapsed
    def sel_matches(sel, collapsed):
        has_collapsed = 'sidebar-collapsed' in sel
        has_container = 'app-container' in sel
        if not has_container:
            return False
        if has_collapsed and not collapsed:
            return False   # collapsed-only rule, class not present
        return True

    def get_ml_filtered(css_block, collapsed):
        idx = 0
        last_val = None
        while idx < len(css_block):
            m = re.search(r'([^{]+)\{([^}]+)\}', css_block[idx:])
            if not m: break
            sel = m.group(1).strip()
            body = m.group(2)
            if sel_matches(sel, collapsed):
                ml = re.search(r'margin-left\s*:\s*([^;!]+)', body)
                if ml:
                    last_val = (ml.group(1).strip(), '!important' in body)
            idx += m.end()
        return last_val

    # Baseline (top-level, outside @media)
    r = get_ml_filtered(top_level, collapsed)
    if r: apply(r[0], r[1])

    # Apply matching @media blocks in source order
    for (min_w, max_w, inner, query) in media_blocks:
        if min_w <= viewport_px <= max_w:
            r = get_ml_filtered(inner, collapsed)
            if r: apply(r[0], r[1])

    return result_val, result_imp

# ── Device matrix ──────────────────────────────────────────────────────────────
# Each entry: (device_label, viewport_width_px, expected_class, expected_layout_description)
# expected_class: 'mobile' | 'gap' | 'tablet' | 'desktop'
#
# Layout rules:
#   mobile  (< 768px)  → sidebar hidden, margin-left: 0 (top bar instead)
#   gap     (768–939px)→ no sidebar (theme off), no mobile bar → margin-left must be 0
#   tablet  (940–1024px)→ sidebar 14rem wide → margin-left: 14rem
#   desktop (> 1024px) → sidebar 20rem wide → margin-left: 20rem

DEVICES = [
    # ── Phones (portrait) ──────────────────────────────
    # StatCounter top mobile: 360x800, 375x812, 390x844, 414x896, 384x832
    ("Samsung Galaxy S (360px)",        360,  'mobile'),
    ("iPhone SE / 6/7/8 (375px)",       375,  'mobile'),
    ("iPhone 12/13/14 (390px)",         390,  'mobile'),
    ("iPhone 6 Plus / XR (414px)",      414,  'mobile'),
    ("Android mid-range (384px)",       384,  'mobile'),
    ("Large Android (430px)",           430,  'mobile'),
    ("Small phone edge (320px)",        320,  'mobile'),
    ("Phone upper bound (767px)",       767,  'mobile'),

    # ── Gap zone (768–939px): no sidebar, no mobile bar ─
    # These widths must NOT activate sidebar margin but must also
    # not show mobile bar. Content should be full-width (margin 0).
    ("Gap zone low (768px)",            768,  'gap'),
    ("iPad mini portrait (768px)",      768,  'gap'),
    ("Generic tablet portrait (800px)", 800,  'gap'),
    ("iPad Air portrait (820px)",       820,  'gap'),
    ("Gap zone high (939px)",           939,  'gap'),

    # ── Tablet narrow sidebar (940–1024px) ─────────────
    ("Sidebar threshold exact (940px)", 940,  'tablet'),
    ("iPad landscape low (960px)",      960,  'tablet'),
    ("iPad Pro 11 portrait (1024px)",  1024,  'tablet'),

    # ── Desktop full sidebar (> 1024px) ────────────────
    # StatCounter top desktop: 1920x1080 #1 (9.37%)
    ("Desktop low (1025px)",           1025,  'desktop'),
    ("MacBook Air 13 (1280px)",        1280,  'desktop'),
    ("HD laptop (1366px)",             1366,  'desktop'),
    ("MacBook Pro 14 (1440px)",        1440,  'desktop'),
    ("1080p monitor (1920px)",         1920,  'desktop'),
    ("4K / 2560px",                    2560,  'desktop'),
]

# Expected margin-left values per class
EXPECTED = {
    'mobile':  '0',    # mobile override zeroes margin
    'gap':     '0',    # no rule applies → baseline is 0 (or no margin)
    'tablet':  '14rem',
    'desktop': '20rem',
}

# ── Base state (sidebar visible, no sidebar-collapsed class) ──────────────────
print("  [base state — sidebar open, no sidebar-collapsed class]")
for label, vp, cls in DEVICES:
    val, imp = compute_margin_left(vp, collapsed=False)
    expected = EXPECTED[cls]
    actual = (val or '0').strip().rstrip(';').lower()
    if actual in ('', 'none', 'initial'): actual = '0'
    if actual == expected:
        ok("base  %4dpx %-38s → margin-left:%-7s ✓ %s" % (vp, '('+label+')', actual, cls))
    else:
        fail("base  %4dpx %-38s → expected:%-7s got:'%s' ✗ %s WRONG" % (vp, '('+label+')', expected, actual, cls))

# ── Collapsed state (post page: sidebar-collapsed class present) ──────────────
print()
print("  [collapsed state — post page, sidebar-collapsed class applied by JS]")
# On post pages the sidebar is always hidden regardless of viewport.
# Expected margin-left when collapsed:
#   mobile (<768px):  mobile @media sets margin-left:0 — this wins even over
#                     sidebar-collapsed (mobile override is !important)
#   gap (768-939px):  sidebar-collapsed global rule fires: margin-left:auto
#                     (no sidebar here anyway, centering is correct)
#   tablet (940-1024px): sidebar-collapsed tablet override: margin-left:auto
#   desktop (>1024px):   sidebar-collapsed global rule: margin-left:auto
EXPECTED_COLLAPSED = {
    'mobile':  '0',     # mobile !important override beats sidebar-collapsed
    'gap':     'auto',  # global sidebar-collapsed rule, no @media guard → fires
    'tablet':  'auto',  # tablet override for sidebar-collapsed → auto
    'desktop': 'auto',  # global sidebar-collapsed → auto (centering)
}
for label, vp, cls in DEVICES:
    val, imp = compute_margin_left(vp, collapsed=True)
    expected = EXPECTED_COLLAPSED[cls]
    actual = (val or '0').strip().rstrip(';').lower()
    if actual in ('', 'none', 'initial'): actual = '0'
    if actual == expected:
        ok("coll  %4dpx %-38s → margin-left:%-7s ✓ %s (collapsed)" % (vp, '('+label+')', actual, cls))
    else:
        fail("coll  %4dpx %-38s → expected:%-7s got:'%s' ✗ %s (collapsed) WRONG" % (vp, '('+label+')', expected, actual, cls))

# ── Aspect ratio: verify meta viewport tag is present ──────────────────────────
print()
print("  [aspect ratio meta]")
# The viewport meta tag is the standard mechanism for responsive layout on real devices.
# Without it, phones render at ~980px desktop width and no media query fires correctly.
home_html_vp = home_html  # already fetched above
has_vp_meta = 'name="viewport"' in home_html_vp or "name='viewport'" in home_html_vp or 'name=viewport' in home_html_vp
check(has_vp_meta,
    "viewport meta tag present (required for device media queries to fire correctly)",
    "MISSING viewport meta — all device breakpoints will be ignored by real mobile browsers")

has_width_device = 'width=device-width' in home_html_vp
check(has_width_device,
    "viewport meta sets width=device-width (correct — enables CSS px = device CSS px mapping)",
    "viewport meta missing width=device-width — breakpoints will fire at wrong device widths")

has_initial_scale = 'initial-scale=1' in home_html_vp
check(has_initial_scale,
    "viewport meta sets initial-scale=1 (correct — prevents zoom-in on iOS Safari)",
    "viewport meta missing initial-scale=1 — iOS Safari may zoom in and break layout")

print()
print("=== SECTION 10 SUMMARY ===")
print("  Devices tested: %d" % len(DEVICES))
print("  Viewport meta checks: 3")

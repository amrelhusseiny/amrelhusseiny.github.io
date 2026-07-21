
import urllib.request, re, sys
BASE = "https://amrelhusseiny.github.io"
PASS = 0
FAIL = 0

def ok(msg): global PASS; PASS += 1; print("  PASS " + msg)
def fail(msg): global FAIL; FAIL += 1; print("  FAIL " + msg)
def check(c, p, f):
    if c: ok(p)
    else: fail(f)

print("Fetching pages...")
blog_html  = urllib.request.urlopen(BASE+"/blog/").read().decode()
m = re.search(r"/css/main\.min\.[^\"'<> ]+\.css", blog_html)
css_url = m.group(0)
css        = urllib.request.urlopen(BASE+css_url).read().decode()
post_url   = BASE+"/blog/001_ai_0003_ai_generated_functional_prints/"
post_html  = urllib.request.urlopen(post_url).read().decode()
home_html  = urllib.request.urlopen(BASE+"/").read().decode()
notes_html = urllib.request.urlopen(BASE+"/notes/").read().decode()
about_html = urllib.request.urlopen(BASE+"/about/").read().decode()
cv_html    = urllib.request.urlopen(BASE+"/cv/").read().decode()
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
check('media="print"' in home_html or "media='print'" in home_html or 'media=print' in home_html,
    "Google Fonts async (media=print swap — render-non-blocking)",
    "Google Fonts is render-blocking (no media=print attribute found)")
check("theme-color"      in home_html,   "theme-color meta tag present",              "theme-color meta missing")
check("og:image"         in home_html,   "og:image meta present",                     "og:image meta missing")

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

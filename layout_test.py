import urllib.request, re, sys

BASE = "https://amrelhusseiny.github.io"
PASS = 0
FAIL = 0

def ok(msg): global PASS; PASS += 1; print("  PASS  " + msg)
def fail(msg): global FAIL; FAIL += 1; print("  FAIL  " + msg)
def check(c, p, f):
    if c: ok(p)
    else: fail(f)

print("Fetching pages and CSS...")
blog_html  = urllib.request.urlopen(BASE+"/blog/").read().decode()
m = re.search(r"/css/main\.min\.[^\"'<> ]+\.css", blog_html)
css_url = m.group(0)
css        = urllib.request.urlopen(BASE+css_url).read().decode()
post_html  = urllib.request.urlopen(BASE+"/blog/001_ai_0003_ai_generated_functional_prints/").read().decode()
home_html  = urllib.request.urlopen(BASE+"/").read().decode()
notes_html = urllib.request.urlopen(BASE+"/notes/").read().decode()
about_html = urllib.request.urlopen(BASE+"/about/").read().decode()
cv_html    = urllib.request.urlopen(BASE+"/cv/").read().decode()
print("CSS: " + css_url + " (" + str(len(css)) + " bytes)")
print()

def get_media(css):
    r = []; i = 0
    while i < len(css):
        m = re.search(r"@media([^{]+)\{", css[i:])
        if not m: break
        q = m.group(1).strip(); s = i + m.end(); d = 1; j = s
        while j < len(css) and d > 0:
            if css[j] == "{": d += 1
            elif css[j] == "}": d -= 1
            j += 1
        r.append((q, css[s:j-1])); i = j
    return r

mb = get_media(css)
def in_media(qp, bp): return [(q,b) for q,b in mb if re.search(qp,q) and bp in b]

# ════ 1. CSS SPECIFICITY ════
print("=== 1. CSS SPECIFICITY ==="); print()
sc_idx = css.find("sidebar-collapsed")
check(sc_idx >= 0, "sidebar-collapsed class in CSS", "sidebar-collapsed MISSING from CSS")
if sc_idx >= 0:
    ctx = css[max(0,sc_idx-100):sc_idx+200]
    check("margin-left:0" in ctx,
        "sidebar-collapsed sets margin-left:0",
        "sidebar-collapsed does NOT set margin-left:0")
    prefix = css[max(0,sc_idx-80):sc_idx+10]
    check("body:not" in prefix,
        "sidebar-collapsed has body:not(.cv-page) prefix — wins specificity vs competing rules",
        "sidebar-collapsed MISSING body:not(.cv-page) prefix — LOSES to body:not(.cv-page) .app-container")
    tb = in_media(r"940px.*1024px|1024px.*940px", "sidebar-collapsed")
    check(len(tb) > 0,
        "sidebar-collapsed override present inside @media(940-1024px) tablet block",
        "sidebar-collapsed NOT in @media(940-1024px) — tablet dead margin when sidebar hidden")

print()

# ════ 2. BREAKPOINTS ════
print("=== 2. BREAKPOINTS ==="); print()
check(any("940px" in q and "max-width" not in q for q,_ in mb),
    "@media(min-width:940px) exists — matches m10c sidebar threshold",
    "MISSING @media(min-width:940px) — wrong threshold")
check(any("940px" in q and "1024px" in q for q,_ in mb),
    "@media(940px-1024px) tablet narrow-sidebar override exists",
    "MISSING @media(940-1024px) tablet override")
check(any("767px" in q or "768px" in q for q,_ in mb),
    "@media(max-width:767px) mobile override exists",
    "MISSING @media(<768px) mobile override")
check(not any("min-width:768px" in q.replace(" ","") and "1024px" in q for q,_ in mb),
    "No rogue min-width:768px tablet rule — dead zone at 768-939px eliminated",
    "ROGUE min-width:768px tablet rule found — dead zone at 768-939px STILL PRESENT")

print()

# ════ 3. HTML ALL PAGE TYPES ════
print("=== 3. HTML — ALL PAGE TYPES ==="); print()
for name, html in [("home",home_html),("blog",blog_html),("post",post_html),("notes",notes_html),("about",about_html)]:
    print("[" + name + "]")
    check("mobile-topbar"    in html, name+": mobile topbar present",     name+": mobile topbar MISSING")
    check("mobile-drawer"    in html, name+": mobile drawer present",     name+": mobile drawer MISSING")
    check("app-sidebar"      in html, name+": desktop sidebar present",   name+": desktop sidebar MISSING")
    check("sam7ToggleDrawer" in html, name+": drawer toggle JS present",  name+": drawer toggle JS MISSING")
    check("sidebar-collapsed" in html,name+": sidebar-collapsed JS present",name+": sidebar-collapsed JS MISSING")

print("[cv] — standalone print layout (no sidebar/mobile expected)")
check("cv-page"  in cv_html, "cv: body.cv-page class applied",   "cv: body.cv-page MISSING")
check("cv.min."  in cv_html, "cv: cv.min CSS loaded separately", "cv: cv.min CSS not found")
check("mermaid" not in cv_html, "cv: no Mermaid loaded",         "cv: Mermaid loaded unnecessarily")
check("mobile-topbar" not in cv_html,
    "cv: no mobile UI (correct — cv/single.html is standalone)",
    "cv: unexpected mobile topbar in standalone layout")

print()

# ════ 4. POST PAGE — SIDEBAR AUTO-COLLAPSES ════
print("=== 4. POST PAGE — SIDEBAR AUTO-COLLAPSES ==="); print()
check(".app-container .post" in post_html,
    "post: querySelector(.app-container .post) detection present",
    "post: .app-container .post detection MISSING — sidebar will NOT auto-hide")
has_post_class = "class=post" in post_html or 'class="post"' in post_html or "class='post'" in post_html
check(has_post_class,
    "post: article has class=post — querySelector detection succeeds",
    "post: article MISSING class=post — querySelector returns null, sidebar never collapses")
hi = post_html.find("sidebar-hidden")
ci = post_html.find("sidebar-collapsed")
check(hi >= 0 and ci >= 0 and abs(hi-ci) < 300,
    "post JS: sidebar-hidden and sidebar-collapsed applied together",
    "post JS: sidebar-hidden and sidebar-collapsed NOT paired in same block")

print()

# ════ 5. SHOW SIDEBAR RESTORE ════
print("=== 5. SHOW SIDEBAR RESTORE ==="); print()
check("sam7ShowSidebar" in post_html, "sam7ShowSidebar function present", "sam7ShowSidebar MISSING")
# Find the function definition (skip the onclick= attribute reference)
si = post_html.find("sam7ShowSidebar")
si2 = post_html.find("sam7ShowSidebar", si+1) if si >= 0 else -1
si = si2 if si2 >= 0 else si  # use the function definition, not the button attribute
if si >= 0:
    sc_ctx = post_html[si:si+600]
    check("sidebar-collapsed" in sc_ctx and "remove" in sc_ctx,
        "sam7ShowSidebar removes sidebar-collapsed (margin restored)",
        "sam7ShowSidebar does NOT remove sidebar-collapsed — content stays shifted after back navigation")
    check("sidebar-hidden" in sc_ctx and "remove" in sc_ctx,
        "sam7ShowSidebar removes sidebar-hidden (sidebar slides back)",
        "sam7ShowSidebar does NOT remove sidebar-hidden — sidebar never returns")

print()

# ════ 6. VIEWPORT MATRIX ════
print("=== 6. VIEWPORT MATRIX ==="); print()
vps = [
    ("360px phone portrait",  "phone"),
    ("430px phone landscape", "phone"),
    ("768px gap low",         "gap"),
    ("820px iPad portrait",   "gap"),
    ("939px gap high",        "gap"),
    ("940px desktop low",     "desk"),
    ("1024px desktop mid",    "desk"),
    ("1280px desktop wide",   "desk"),
    ("1440px desktop HD",     "desk"),
    ("1920px full HD",        "desk"),
]
for label, kind in vps:
    if kind == "phone":
        check(len(in_media(r"max-width.*767|767.*max-width", "margin-left")) > 0,
            label+": @media(<768px) zeroes margin-left — no sidebar dead zone",
            label+": mobile margin-left reset MISSING")
    elif kind == "gap":
        rogue = [q for q,b in mb if re.search(r"min-width\s*:\s*768", q) and "1024px" in q and "margin-left" in b]
        check(len(rogue) == 0,
            label+": no margin-left rule active — content fills full width (no dead zone)",
            label+": ROGUE 768px margin-left rule — dead zone present: " + str(rogue))
    elif kind == "desk":
        check(len(in_media(r"min-width.*940", "margin-left")) > 0,
            label+": @media(>=940px) provides sidebar margin-left",
            label+": desktop sidebar margin MISSING")
        collapsed_ok = (len(in_media(r"940px.*1024px|1024px.*940px", "sidebar-collapsed")) > 0
                        or ("body:not" in css[max(0,sc_idx-80):sc_idx+10] if sc_idx >= 0 else False))
        check(collapsed_ok,
            label+": sidebar-collapsed wins cascade at desktop widths",
            label+": sidebar-collapsed LOSES cascade — dead margin persists on posts at this width")

print()

# ════ 7. NOTES / MERMAID ════
print("=== 7. NOTES / MERMAID ==="); print()
check("mermaid.min.js" in notes_html, "notes: Mermaid CDN script present", "notes: Mermaid MISSING")
check("defer" in notes_html and "mermaid" in notes_html, "notes: Mermaid deferred", "notes: Mermaid NOT deferred")
check("sam7InitMermaid" in notes_html, "notes: sam7InitMermaid present", "notes: sam7InitMermaid MISSING")
check("mermaid" not in blog_html, "blog: no Mermaid loaded", "blog: Mermaid loaded unnecessarily")
check("mermaid" not in home_html, "home: no Mermaid loaded", "home: Mermaid loaded unnecessarily")

print()

# ════ 8. PERFORMANCE ════
print("=== 8. PERFORMANCE ==="); print()
check("favicon-64.png" in home_html, "favicon self-hosted", "favicon on external CDN")
check("islamic_bg.webp" in home_html, "WebP bg preloaded", "WebP bg missing")
check("media=print" in home_html or "media='print'" in home_html or 'media="print"' in home_html,
    "Google Fonts loaded async (media=print)", "Google Fonts render-blocking")
check("theme-color" in home_html, "theme-color meta present", "theme-color meta missing")
check("og:image" in home_html, "og:image meta present", "og:image meta missing")

print()

# ════ SUMMARY ════
print("=== SUMMARY ===")
t = PASS + FAIL
print("  Passed: " + str(PASS) + "/" + str(t))
print("  Failed: " + str(FAIL) + "/" + str(t))
if FAIL > 0:
    print("\n  RESULT: FAILING")
    sys.exit(1)
else:
    print("\n  RESULT: ALL PASS")

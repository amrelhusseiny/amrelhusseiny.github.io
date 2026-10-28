/* Client behaviour: snackbar, lightbox, back-to-top, mermaid */

/* Snackbar (flat catalog notice) */
let snackTimer: number | undefined;
function showSnackbar(msg: string) {
  let el = document.querySelector('.snackbar') as HTMLElement | null;
  if (!el) {
    el = document.createElement('div');
    el.className = 'snackbar';
    el.setAttribute('role', 'status');
    document.body.appendChild(el);
  }
  el.textContent = msg;
  requestAnimationFrame(() => el!.classList.add('show'));
  if (snackTimer) window.clearTimeout(snackTimer);
  snackTimer = window.setTimeout(() => { el?.classList.remove('show'); }, 2200);
}
(window as any).showSnackbar = showSnackbar;

/* Theme toggle */
function themeInit() {
  const root = document.documentElement;
  const btn = document.querySelector('[data-theme-toggle]') as HTMLElement | null;
  const label = btn?.querySelector('[data-theme-label]');
  const meta = document.querySelector('meta[name="theme-color"]');

  const sync = () => {
    const dark = root.getAttribute('data-theme') === 'dark';
    if (label) label.textContent = dark ? 'Light' : 'Dark';
    if (btn) {
      btn.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
      btn.setAttribute('aria-pressed', String(dark));
    }
    if (meta) meta.setAttribute('content', dark ? '#0c0c0c' : '#ececec');
  };

  sync();
  btn?.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('amro_blog_theme', next); } catch (e) {}
    sync();
  });
}

/* Back to top */
function backTopInit() {
  const btn = document.querySelector('[data-back-to-top]');
  if (!btn) return;
  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 600);
  }, { passive: true });
  btn.addEventListener('click', () => window.scrollTo({ top: 0 }));
}

/* Lightbox */
function lightboxInit() {
  const dialog = document.getElementById('lightbox') as HTMLDialogElement | null;
  const img = document.getElementById('lightbox-img') as HTMLImageElement | null;
  if (!dialog || !img) return;

  const open = (src: string, alt: string) => {
    img.src = src;
    img.alt = alt;
    dialog.showModal();
  };

  document.addEventListener('click', (e) => {
    const t = (e.target as HTMLElement).closest('.lightbox-trigger, .post-content img, .note-card-content img');
    if (!t || dialog.open) return;
    e.preventDefault();
    const src = t.getAttribute('data-src') || (t as HTMLImageElement).src;
    const alt = t.getAttribute('data-alt') || t.getAttribute('alt') || '';
    if (src) open(src, alt);
  });

  dialog.addEventListener('click', (e) => {
    if (e.target === dialog) dialog.close();
  });
  dialog.querySelector('.lightbox-close')?.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => { img.src = ''; img.alt = ''; });
}

document.addEventListener('DOMContentLoaded', () => {
  themeInit();
  backTopInit();
  lightboxInit();
});

/* Mermaid: render code blocks emitted by Astro (pre[data-language="mermaid"]) */
async function mermaidInit() {
  const blocks = document.querySelectorAll('pre[data-language="mermaid"]');
  if (!blocks.length) return;
  try {
    const { default: mermaid } = await import("mermaid");
    mermaid.initialize({
      startOnLoad: false,
      theme: "base",
      securityLevel: "strict",
      fontFamily: '"Geist Mono", monospace',
      themeVariables: {
        primaryColor: "#ffffff",
        primaryTextColor: "#000000",
        primaryBorderColor: "#000000",
        secondaryColor: "#f3f3f3",
        tertiaryColor: "#ececec",
        lineColor: "#000000",
        textColor: "#000000",
        fontSize: "13px",
      },
    });
    for (const pre of blocks) {
      const code = pre.querySelector("code");
      if (!code) continue;
      let src = code.textContent || "";
      // strip embedded YAML frontmatter that Astro kept as literal text
      src = src.replace(/^\s*---[\s\S]*?---\s*/, "").trim();
      const id = "m" + Math.random().toString(36).slice(2, 10);
      try {
        const { svg } = await mermaid.render(id, src);
        const div = document.createElement("div");
        div.className = "mermaid-figure";
        div.innerHTML = svg;
        pre.replaceWith(div);
      } catch (e) {
        console.warn("mermaid render failed", e);
      }
    }
  } catch (e) {
    console.warn("mermaid load failed", e);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  mermaidInit();
});

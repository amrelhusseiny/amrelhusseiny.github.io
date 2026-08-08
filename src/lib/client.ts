/* Client behaviour: theme, lightbox, progress, reveal, back-to-top */

/* M3 Snackbar */
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
  const html = document.documentElement;
  const btn = document.querySelector('[data-theme-toggle]');
  const label = document.querySelector('[data-theme-label]');
  const sun = document.querySelector('[data-theme-icon-sun]');
  const moon = document.querySelector('[data-theme-icon-moon]');
  const sync = () => {
    const dark = html.getAttribute('data-theme') === 'dark';
    if (label) label.textContent = dark ? 'Dark mode' : 'Light mode';
    if (sun) sun.style.display = dark ? 'none' : 'block';
    if (moon) moon.style.display = dark ? 'block' : 'none';
    const tc = document.querySelector('meta[name="theme-color"]');
    if (tc) tc.setAttribute('content', dark ? '#101010' : '#ffffff');
  };
  sync();
  btn?.addEventListener('click', () => {
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('amro_blog_theme', next);
    sync();
  });
}

/* Reading progress bar */
function progressInit() {
  const bar = document.querySelector('[data-progress]');
  if (!bar) return;
  const update = () => {
    const h = document.documentElement;
    const max = h.scrollHeight - h.clientHeight;
    bar.style.transform = `scaleX(${max > 0 ? window.scrollY / max : 0})`;
  };
  window.addEventListener('scroll', update, { passive: true });
  update();
}

/* Back to top */
function backTopInit() {
  const btn = document.querySelector('[data-back-to-top]');
  if (!btn) return;
  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 600);
  }, { passive: true });
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
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

/* Reveal on scroll */
function revealInit() {
  const els = document.querySelectorAll('[data-reveal]');
  if (!els.length) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) { els.forEach((el) => el.classList.add('revealed')); return; }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (en.isIntersecting) {
        en.target.classList.add('revealed');
        io.unobserve(en.target);
      }
    });
  }, { threshold: 0 });
  els.forEach((el) => io.observe(el));
}

/* M3 ripple (Web Animations API) */
function rippleInit() {
  const els = document.querySelectorAll('[data-ripple]');
  if (!els.length) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) return;

  els.forEach((el) => {
    el.addEventListener('pointerdown', (e) => {
      const rect = (el as HTMLElement).getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = (e as PointerEvent).clientX - rect.left - size / 2;
      const y = (e as PointerEvent).clientY - rect.top - size / 2;
      const ripple = document.createElement('span');
      ripple.className = 'ripple';
      ripple.style.width = ripple.style.height = `${size}px`;
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;
      el.appendChild(ripple);
      ripple.addEventListener('animationend', () => ripple.remove());
    });
  });
}

/* Active nav highlight */
function navActiveInit() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach((a) => {
    const href = a.getAttribute('href') || '';
    if (href && href !== '/' && path.startsWith(href)) a.classList.add('active');
  });
}

document.addEventListener('DOMContentLoaded', () => {
  themeInit();
  progressInit();
  backTopInit();
  lightboxInit();
  revealInit();
  rippleInit();
  navActiveInit();
});

/* Auto-hide nav on scroll down, reappear on scroll up */
function navHideInit() {
  const nav = document.querySelector('.nav-drawer');
  if (!nav) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) return;

  let lastY = window.scrollY;
  let ticking = false;

  const update = () => {
    const y = window.scrollY;
    const delta = y - lastY;
    lastY = y;
    // Hide only when scrolling down past 120px; show when scrolling up (or near top)
    if (y > 120 && delta > 4) {
      nav.classList.add('nav-hidden');
    } else if (delta < -4 || y <= 120) {
      nav.classList.remove('nav-hidden');
    }
    ticking = false;
  };

  window.addEventListener('scroll', () => {
    if (!ticking) {
      window.requestAnimationFrame(update);
      ticking = true;
    }
  }, { passive: true });
}

document.addEventListener('DOMContentLoaded', () => {
  navHideInit();
});

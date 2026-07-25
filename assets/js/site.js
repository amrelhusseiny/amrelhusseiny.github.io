/* Amro's Blog — site.js (Material Design 3)
   Deferred. Runs after HTML is parsed. */

/* ── Theme toggle ── */
function sam7ToggleTheme() {
  var html = document.documentElement;
  var next = (html.getAttribute('data-theme') || 'light') === 'light' ? 'dark' : 'light';
  html.setAttribute('data-theme', next);
  localStorage.setItem('amro_blog_theme', next);
  _sam7SyncThemeUI(next);
}
function _sam7SyncThemeUI(t) {
  var icon  = t === 'dark' ? '\u263E' : '\u2600';
  var label = t === 'dark' ? 'Dark mode' : 'Light mode';
  /* Drawer */
  var ti = document.getElementById('theme-icon');
  var tl = document.getElementById('theme-label');
  if (ti) ti.textContent = icon;
  if (tl) tl.textContent = label;
  /* Rail */
  var ri = document.getElementById('rail-theme-icon');
  if (ri) ri.textContent = icon;
  /* Mobile nav bar */
  var nb = document.getElementById('nav-theme-icon');
  if (nb) nb.textContent = icon;
}

/* ── M3 Ripple (Web Animations API) ── */
(function () {
  var GROW_MS  = 400;
  var MIN_MS   = 200;
  var EASING   = 'cubic-bezier(0.2, 0, 0, 1)';

  function attachRipple(el) {
    if (el._m3ripple) return;
    el._m3ripple = true;
    el.style.position = el.style.position || 'relative';
    el.style.overflow = 'hidden';

    var surface = document.createElement('span');
    surface.setAttribute('aria-hidden', 'true');
    surface.style.cssText = [
      'position:absolute', 'inset:0', 'border-radius:inherit',
      'pointer-events:none', 'overflow:hidden'
    ].join(';');
    el.appendChild(surface);

    var growAnim = null;
    var pressedAt = 0;

    function startPress(evt) {
      var rect = el.getBoundingClientRect();
      var zoom = el.currentCSSZoom || 1;
      var maxDim = Math.max(rect.width, rect.height);
      var initSize = Math.floor(maxDim * 0.2 / zoom);
      var hypo = Math.sqrt(rect.width * rect.width + rect.height * rect.height);
      var finalScale = ((hypo + 10 + maxDim * 0.35) / initSize) / zoom;
      var cx, cy;
      if (evt && evt.clientX !== undefined) {
        cx = (evt.clientX - rect.left) / zoom - initSize / 2;
        cy = (evt.clientY - rect.top) / zoom - initSize / 2;
      } else {
        cx = (rect.width / zoom - initSize) / 2;
        cy = (rect.height / zoom - initSize) / 2;
      }
      var endX = (rect.width / zoom - initSize) / 2;
      var endY = (rect.height / zoom - initSize) / 2;

      if (growAnim) growAnim.cancel();
      pressedAt = performance.now();

      growAnim = surface.animate([
        { top: '0', left: '0',
          width: initSize + 'px', height: initSize + 'px',
          transform: 'translate(' + cx + 'px,' + cy + 'px) scale(1)',
          background: 'var(--md-color-on-surface)',
          opacity: '0.12' },
        { top: '0', left: '0',
          width: initSize + 'px', height: initSize + 'px',
          transform: 'translate(' + endX + 'px,' + endY + 'px) scale(' + finalScale + ')',
          background: 'var(--md-color-on-surface)',
          opacity: '0.12' }
      ], { duration: GROW_MS, easing: EASING, fill: 'forwards', pseudoElement: null });
    }

    function endPress() {
      var elapsed = performance.now() - pressedAt;
      var delay = Math.max(0, MIN_MS - elapsed);
      setTimeout(function () {
        if (!growAnim) return;
        growAnim.cancel();
        growAnim = null;
        surface.animate([
          { opacity: '0.12' },
          { opacity: '0' }
        ], { duration: 150, easing: EASING, fill: 'forwards' });
      }, delay);
    }

    el.addEventListener('pointerdown', function (e) {
      if (!e.isPrimary) return;
      startPress(e);
      el.setPointerCapture(e.pointerId);
    });
    el.addEventListener('pointerup',     endPress);
    el.addEventListener('pointercancel', function () { if (growAnim) { growAnim.cancel(); growAnim = null; } });
  }

  window.m3AttachRipple = attachRipple;
})();

/* ── Sidebar show (float btn on post pages) ── */
function sam7ShowSidebar() {
  var sidebar  = document.getElementById('app-sidebar');
  var floatBtn = document.getElementById('sidebar-float-btn');
  if (!sidebar) return;
  sidebar.classList.remove('sidebar-hidden');
  document.querySelector('.app-container').classList.remove('sidebar-collapsed');
  if (floatBtn) floatBtn.style.display = 'none';
}

/* ── DOM ready ── */
document.addEventListener('DOMContentLoaded', function () {

  /* Sync theme UI */
  var t = document.documentElement.getAttribute('data-theme') || 'light';
  _sam7SyncThemeUI(t);

  /* Active nav highlight -- drawer, rail, bottom nav bar */
  var path = window.location.pathname;
  document.querySelectorAll(
    '.app-header-menu a, #nav-rail .rail-item, #mobile-nav-bar .m3-nav-item'
  ).forEach(function (a) {
    var href = a.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) a.classList.add('nav-active');
  });

  /* M3: drawer is persistent on expanded layout -- no auto-hide on post pages */
  /* Post-card clicks: navigate directly, drawer stays visible */
  document.querySelectorAll('.post-card').forEach(function (card) {
    card.addEventListener('click', function (e) {
      e.preventDefault();
      window.location.href = card.getAttribute('href');
    });
  });

  /* Attach M3 ripple to interactive elements */
  document.querySelectorAll(
    '.post-card, .sidebar-blog-link, .sidebar-notes-link, ' +
    '.sidebar-about-link, .sidebar-cv-link, .sidebar-ctrl-btn, ' +
    '.share-btn, .about-btn, .m3-nav-item, .notes-tl-link, ' +
    '.notes-tl-mobile-chip, .sidebar-tag, .rail-item'
  ).forEach(window.m3AttachRipple);

});

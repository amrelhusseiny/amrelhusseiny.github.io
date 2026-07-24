/* Amro's Blog — site.js
   Loaded with defer — runs after HTML is parsed, before DOMContentLoaded fires. */

/* ── Theme toggle ── */
function sam7ToggleTheme() {
  var html = document.documentElement;
  var next = (html.getAttribute('data-theme') || 'light') === 'light' ? 'dark' : 'light';
  html.setAttribute('data-theme', next);
  localStorage.setItem('amro_blog_theme', next);
  _sam7SyncThemeUI(next);
}
function _sam7SyncThemeUI(t) {
  var ti = document.getElementById('theme-icon');
  var tl = document.getElementById('theme-label');
  var di = document.getElementById('drawer-theme-icon');
  var dl = document.getElementById('drawer-theme-label');
  if (ti) ti.textContent = t === 'dark' ? '\u263E' : '\u2600';
  if (tl) tl.textContent = t === 'dark' ? 'Dark Theme' : 'Light Theme';
  if (di) di.textContent = t === 'dark' ? '\u263E' : '\u2600';
  if (dl) dl.textContent = t === 'dark' ? 'Dark' : 'Light';
}

/* ── Mobile drawer ── */
var _amroDrawerOpen = false;
function sam7ToggleDrawer() { _amroDrawerOpen ? sam7CloseDrawer() : sam7OpenDrawer(); }
function sam7OpenDrawer() {
  _amroDrawerOpen = true;
  document.getElementById('mobile-drawer').classList.add('drawer-open');
  document.getElementById('mobile-backdrop').classList.add('backdrop-visible');
  document.getElementById('hamburger-icon').textContent = '\u2715';
}
function sam7CloseDrawer() {
  _amroDrawerOpen = false;
  document.getElementById('mobile-drawer').classList.remove('drawer-open');
  document.getElementById('mobile-backdrop').classList.remove('backdrop-visible');
  document.getElementById('hamburger-icon').textContent = '\u2630';
}

/* ── Sidebar show (float button) ── */
function sam7ShowSidebar() {
  var sidebar  = document.getElementById('app-sidebar');
  var floatBtn = document.getElementById('sidebar-float-btn');
  sidebar.classList.remove('sidebar-hidden');
  document.querySelector('.app-container').classList.remove('sidebar-collapsed');
  if (floatBtn) floatBtn.style.display = 'none';
}


/* ── DOM ready ── */
document.addEventListener('DOMContentLoaded', function() {
  /* sync theme UI */
  var t = document.documentElement.getAttribute('data-theme') || 'light';
  _sam7SyncThemeUI(t);

  /* active nav highlight */
  var path = window.location.pathname;
  document.querySelectorAll('.app-header-menu a, #mobile-drawer .drawer-nav a').forEach(function(a) {
    var href = a.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) a.classList.add('nav-active');
  });

  /* close drawer on nav link click */
  document.querySelectorAll('#mobile-drawer .drawer-nav a').forEach(function(a) {
    a.addEventListener('click', function() { sam7CloseDrawer(); });
  });

  /* sidebar behaviour on post pages */
  var sidebar  = document.getElementById('app-sidebar');
  var floatBtn = document.getElementById('sidebar-float-btn');
  if (document.querySelector('.app-container .post')) {
    sidebar.classList.add('sidebar-hidden');
    document.querySelector('.app-container').classList.add('sidebar-collapsed');
    if (floatBtn) floatBtn.style.display = 'flex';
  }

  /* D: post-card clicks — no artificial delay, navigate immediately */
  document.querySelectorAll('.post-card').forEach(function(card) {
    card.addEventListener('click', function(e) {
      e.preventDefault();
      var href = card.getAttribute('href');
      sidebar.classList.add('sidebar-hidden');
      document.querySelector('.app-container').classList.add('sidebar-collapsed');
      window.location.href = href;
    });
  });
});

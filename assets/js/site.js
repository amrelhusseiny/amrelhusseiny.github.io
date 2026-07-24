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

/* ── Particle engine — lazy loaded on first click ── */
var _amroParticlesLoaded = false;
var _p = { enabled: false, frame: null, bubbles: [], orbs: [] };

function sam7ToggleParticles() {
  if (!_amroParticlesLoaded) {
    _amroParticlesLoaded = true;
  }
  _p.enabled = !_p.enabled;
  var canvas = document.getElementById('sam7-particles');
  var btn    = document.getElementById('ambient-toggle-btn');
  var lbl    = document.getElementById('ambient-label');
  var dbtn   = document.getElementById('drawer-ambient-btn');
  var dlbl   = document.getElementById('drawer-ambient-label');
  if (_p.enabled) {
    canvas.style.display = 'block';
    if (btn)  btn.classList.add('ambient-on');
    if (dbtn) dbtn.classList.add('ambient-on');
    if (lbl)  lbl.textContent  = 'Ambient On';
    if (dlbl) dlbl.textContent = 'Ambient On';
    _sam7InitParticles(); _sam7DrawParticles();
  } else {
    cancelAnimationFrame(_p.frame);
    canvas.style.display = 'none';
    if (btn)  btn.classList.remove('ambient-on');
    if (dbtn) dbtn.classList.remove('ambient-on');
    if (lbl)  lbl.textContent  = 'Ambient Mode';
    if (dlbl) dlbl.textContent = 'Ambient';
    var ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
}

function _sam7InitParticles() {
  var canvas = document.getElementById('sam7-particles');
  canvas.width = window.innerWidth; canvas.height = window.innerHeight;
  var w = canvas.width, h = canvas.height;
  var dk = document.documentElement.getAttribute('data-theme') === 'dark';
  _p.orbs = [
    {x:w*.25,y:h*.3,r:w*.22,vx:.15,vy:.10,a:0,c1:dk?'rgba(34,211,238,0.07)':'rgba(6,182,212,0.13)'},
    {x:w*.75,y:h*.4,r:w*.26,vx:-.12,vy:.08,a:1,c1:dk?'rgba(139,92,246,0.07)':'rgba(16,185,129,0.11)'},
    {x:w*.5,y:h*.8,r:w*.24,vx:.08,vy:-.15,a:2,c1:dk?'rgba(236,72,153,0.05)':'rgba(99,102,241,0.09)'}
  ];
  _p.bubbles = [];
  for (var i = 0; i < 18; i++) {
    _p.bubbles.push({
      x:Math.random()*w, y:Math.random()*h,
      s:Math.random()*12+4, vx:(Math.random()-.5)*.35, vy:(Math.random()-.5)*.35,
      op:Math.random()*.22+.08, a:Math.random()*Math.PI*2, sp:(Math.random()-.5)*.006
    });
  }
}

function _sam7DrawParticles() {
  var canvas = document.getElementById('sam7-particles');
  if (!canvas || !_p.enabled) return;
  var ctx = canvas.getContext('2d'), w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  _p.orbs.forEach(function(o) {
    o.x+=o.vx; o.y+=o.vy; o.a+=.0015;
    if (o.x-o.r<0||o.x+o.r>w) o.vx*=-1;
    if (o.y-o.r<0||o.y+o.r>h) o.vy*=-1;
    var r = o.r*(1+Math.sin(o.a)*.1);
    var g = ctx.createRadialGradient(o.x,o.y,0,o.x,o.y,r);
    g.addColorStop(0,o.c1); g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.beginPath(); ctx.arc(o.x,o.y,r,0,Math.PI*2); ctx.fill();
  });
  _p.bubbles.forEach(function(b) {
    b.x+=b.vx; b.y+=b.vy; b.a+=b.sp;
    if (b.x<-20) b.x=w+20; if (b.x>w+20) b.x=-20;
    if (b.y<-20) b.y=h+20; if (b.y>h+20) b.y=-20;
    ctx.save(); ctx.globalAlpha=b.op;
    ctx.translate(b.x,b.y); ctx.rotate(b.a);
    var gr = ctx.createRadialGradient(-b.s*.2,-b.s*.2,0,0,0,b.s);
    gr.addColorStop(0,'rgba(255,255,255,0.14)');
    gr.addColorStop(.8,'rgba(255,255,255,0.02)');
    gr.addColorStop(1,'rgba(255,255,255,0.10)');
    ctx.fillStyle=gr; ctx.beginPath(); ctx.arc(0,0,b.s,0,Math.PI*2); ctx.fill();
    ctx.strokeStyle='rgba(255,255,255,0.38)'; ctx.lineWidth=.7;
    ctx.beginPath(); ctx.arc(0,0,b.s-.5,-Math.PI*.75,-Math.PI*.25); ctx.stroke();
    ctx.fillStyle='#fff'; ctx.beginPath();
    ctx.arc(-b.s*.42,-b.s*.42,b.s*.11,0,Math.PI*2); ctx.fill();
    ctx.restore();
  });
  _p.frame = requestAnimationFrame(_sam7DrawParticles);
}
window.addEventListener('resize', function() { if (_p.enabled) _sam7InitParticles(); });

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

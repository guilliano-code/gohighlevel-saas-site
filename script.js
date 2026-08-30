/* FLOWSA — shared site script. Every handler guards for missing elements
   so the same file can run unchanged on every page. */

if (history.scrollRestoration) history.scrollRestoration = 'manual';
window.scrollTo(0, 0);

var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ── SCROLL PROGRESS BAR ─────────────────────────── */
(function () {
  var bar = document.createElement('div');
  bar.className = 'scroll-progress';
  bar.setAttribute('aria-hidden', 'true');
  document.body.prepend(bar);
  var raf = 0;
  function update() {
    raf = 0;
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    bar.style.transform = 'scaleX(' + (max > 0 ? h.scrollTop / max : 0) + ')';
  }
  function onScroll() {
    if (!raf) raf = requestAnimationFrame(update);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  update();
})();

/* ── MAGNETIC BUTTONS ─────────────────────────────── */
(function () {
  if (prefersReducedMotion || window.matchMedia('(pointer: coarse)').matches) return;
  var pull = 0.28, maxPull = 9;
  document.querySelectorAll('.btn-primary, .btn-ghost').forEach(function (el) {
    el.addEventListener('mousemove', function (e) {
      var r = el.getBoundingClientRect();
      var dx = Math.max(-maxPull, Math.min(maxPull, (e.clientX - (r.left + r.width / 2)) * pull));
      var dy = Math.max(-maxPull, Math.min(maxPull, (e.clientY - (r.top + r.height / 2)) * pull));
      el.style.transform = 'translate(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px)';
    });
    el.addEventListener('mouseleave', function () { el.style.transform = ''; });
  });
})();

/* ── ANIMATED STAT COUNTERS ───────────────────────── */
(function () {
  var stats = document.querySelectorAll('.stat-num[data-count-to]');
  if (!stats.length) return;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      var el = entry.target;
      io.unobserve(el);
      var to = parseFloat(el.dataset.countTo);
      var decimals = el.dataset.countTo.indexOf('.') > -1 ? 1 : 0;
      var suffix = el.dataset.countSuffix || '';
      if (prefersReducedMotion) { el.textContent = to.toFixed(decimals) + suffix; return; }
      var start = performance.now(), duration = 1100;
      function step(now) {
        var t = Math.min((now - start) / duration, 1);
        var eased = 1 - Math.pow(1 - t, 3);
        el.textContent = (to * eased).toFixed(decimals) + suffix;
        if (t < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    });
  }, { threshold: 0.5 });
  stats.forEach(function (el) { io.observe(el); });
})();

/* ── HERO VIDEO PARALLAX ──────────────────────────── */
(function () {
  if (prefersReducedMotion) return;
  var thumb = document.querySelector('.vsl-thumb');
  if (!thumb) return;
  var raf = 0;
  function onScroll() {
    if (raf) return;
    raf = requestAnimationFrame(function () {
      var rect = thumb.getBoundingClientRect();
      var offset = (rect.top - window.innerHeight / 2) * 0.06;
      thumb.style.transform = 'scale(1.08) translateY(' + offset.toFixed(1) + 'px)';
      raf = 0;
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

/* Prevent iOS zoom on form inputs */
(function () {
  var vp = document.querySelector('meta[name="viewport"]');
  if (!vp) return;
  document.addEventListener('focusin', function (e) {
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName))
      vp.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0';
  });
  document.addEventListener('focusout', function (e) {
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName))
      vp.content = 'width=device-width, initial-scale=1.0';
  });
})();

/* ── FADE IN on scroll ──────────────────────────── */
(function () {
  var targets = document.querySelectorAll('.fade-up');
  if (!targets.length) return;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        var d = parseInt(e.target.dataset.delay || '0', 10);
        e.target.style.transitionDelay = d + 'ms';
        e.target.classList.add('visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: window.innerWidth < 640 ? 0.05 : 0.1 });
  targets.forEach(function (el) { io.observe(el); });
})();

/* ── FAQ ────────────────────────────────────────── */
function toggleFaq(btn) {
  var item = btn.parentElement;
  var isOpen = item.classList.contains('open');
  document.querySelectorAll('.faq-item.open').forEach(function (el) { el.classList.remove('open'); });
  if (!isOpen) item.classList.add('open');
}

/* ── VSL PLAY ───────────────────────────────────── */
var vslLeadSubmitted = false;
try { vslLeadSubmitted = localStorage.getItem('vslLeadSubmitted') === '1'; } catch (err) {}

function playVsl() {
  if (!vslLeadSubmitted) {
    var modal = document.getElementById('vsl-modal-overlay');
    if (modal) {
      modal.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    return;
  }
  var overlay = document.getElementById('vsl-overlay');
  var video = document.getElementById('vsl-video');
  if (!overlay || !video) return;
  overlay.classList.add('hidden');
  if (!video.src) { video.src = 'vsl-v1.mp4'; video.load(); }
  video.play();
}

document.addEventListener('DOMContentLoaded', function () {
  var video = document.getElementById('vsl-video');
  if (video) {
    video.addEventListener('click', function () {
      if (video.paused) { video.play(); } else { video.pause(); }
    });
  }

  var modalOverlay = document.getElementById('vsl-modal-overlay');
  if (modalOverlay) {
    modalOverlay.addEventListener('click', function (e) {
      if (e.target === this) {
        this.classList.remove('open');
        document.body.style.overflow = '';
      }
    });
  }

  var form = document.getElementById('vsl-lead-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var inputs = form.querySelectorAll('[required]');
      var valid = true;
      inputs.forEach(function (el) {
        if (el.offsetParent === null) return; /* skip hidden fields */
        if (!el.value.trim()) { el.focus(); valid = false; }
      });
      if (!valid) return;

      vslLeadSubmitted = true;
      try { localStorage.setItem('vslLeadSubmitted', '1'); } catch (err) {}
      if (modalOverlay) {
        modalOverlay.classList.remove('open');
        document.body.style.overflow = '';
      }

      var overlay = document.getElementById('vsl-overlay');
      var vid = document.getElementById('vsl-video');
      if (overlay && vid) {
        overlay.classList.add('hidden');
        if (!vid.src) { vid.src = 'vsl-v1.mp4'; vid.load(); }
        vid.play();
      }
    });
  }
});

/* ── BILLING TOGGLE ─────────────────────────────── */
var billing = 'yearly';

var PRICES = {
  basis:   { monthly: 60,  yearly: 48  },
  starter: { monthly: 120, yearly: 96  },
  pro:     { monthly: 200, yearly: 160 },
};

function animateCount(elId, fromVal, toVal, duration) {
  var el = document.getElementById(elId);
  if (!el) return;
  var start = performance.now();
  var diff = toVal - fromVal;
  function step(now) {
    var t = Math.min((now - start) / duration, 1);
    var e = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    el.textContent = Math.round(fromVal + diff * e);
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function setBilling(mode) {
  if (mode === billing) return;
  billing = mode;
  var yearly = mode === 'yearly';

  var tabMonthly = document.getElementById('tab-monthly');
  var tabYearly = document.getElementById('tab-yearly');
  if (!tabMonthly || !tabYearly) return;
  tabMonthly.classList.toggle('active', !yearly);
  tabYearly.classList.toggle('active', yearly);

  document.getElementById('basis-billing-label').classList.toggle('faded', yearly);
  document.getElementById('starter-billing-label').classList.toggle('faded', yearly);
  document.getElementById('pro-billing-label').classList.toggle('faded', yearly);

  animateCount('basis-price', yearly ? PRICES.basis.monthly : PRICES.basis.yearly, yearly ? PRICES.basis.yearly : PRICES.basis.monthly, 480);
  animateCount('starter-price', yearly ? PRICES.starter.monthly : PRICES.starter.yearly, yearly ? PRICES.starter.yearly : PRICES.starter.monthly, 480);
  animateCount('pro-price', yearly ? PRICES.pro.monthly : PRICES.pro.yearly, yearly ? PRICES.pro.yearly : PRICES.pro.monthly, 480);

  var bNote = document.getElementById('basis-yearly-note');
  var sNote = document.getElementById('starter-yearly-note');
  var pNote = document.getElementById('pro-yearly-note');

  if (yearly) {
    bNote.textContent = '€576 per jaar gefactureerd, je bespaart €144';
    sNote.textContent = '€1.152 per jaar gefactureerd, je bespaart €288';
    pNote.textContent = '€1.920 per jaar gefactureerd, je bespaart €480';
    bNote.classList.remove('hidden');
    sNote.classList.remove('hidden');
    pNote.classList.remove('hidden');
  } else {
    bNote.classList.add('hidden');
    sNote.classList.add('hidden');
    pNote.classList.add('hidden');
  }
}

/* ── MOBILE PLAN SWITCHER ───────────────────────── */
function switchPlan(plan) {
  document.querySelectorAll('.pricing-grid .price-card-wrap[data-plan]').forEach(function (el) {
    el.classList.toggle('plan-active', el.dataset.plan === plan);
  });
  document.querySelectorAll('.plan-switch-btn').forEach(function (btn) {
    btn.classList.toggle('active', btn.dataset.plan === plan);
  });
}
if (document.querySelector('.plan-switcher') && window.innerWidth <= 620) switchPlan('plus');
window.addEventListener('resize', function () {
  if (document.querySelector('.plan-switcher') && window.innerWidth <= 620) {
    var active = document.querySelector('.plan-switch-btn.active');
    switchPlan(active ? active.dataset.plan : 'plus');
  }
});

/* ── CONTACT FORM ───────────────────────────────── */
(function () {
  var form = document.getElementById('contact-form-main');
  if (!form) return;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var naam    = form.querySelector('[name="naam"]').value.trim();
    var bedrijf = form.querySelector('[name="bedrijf"]').value.trim();
    var tel     = form.querySelector('[name="telefoon"]').value.trim();
    var email   = form.querySelector('[name="email"]').value.trim();
    var bericht = form.querySelector('[name="bericht"]').value.trim();
    var subject = encodeURIComponent('Nieuwe aanvraag van ' + naam + ' (' + bedrijf + ')');
    var body    = encodeURIComponent('Naam: ' + naam + '\nBedrijf: ' + bedrijf + '\nTelefoon: ' + tel + '\nE-mail: ' + email + '\n\nBericht:\n' + bericht);
    window.location.href = 'mailto:Guilliano@dailyshotsmedia.com?subject=' + subject + '&body=' + body;
    var success = document.getElementById('contact-success');
    if (success) success.style.display = 'block';
    form.reset();
  });
})();

/* ── COMPARE PLANS TOGGLE ──────────────────────── */
function toggleCompare() {
  var btn = document.getElementById('compare-btn');
  var wrap = document.getElementById('compare-table-wrap');
  if (!btn || !wrap) return;
  var open = wrap.classList.toggle('open');
  btn.classList.toggle('open', open);
  btn.querySelector('.cmp-chevron').style.transform = open ? 'rotate(180deg)' : '';
}

/* ── MOBILE MENU TOGGLE ─────────────────────────── */
(function () {
  var btn = document.getElementById('hamburger-btn');
  var menu = document.getElementById('mobile-menu');
  if (!btn || !menu) return;

  function closeMenu() {
    btn.classList.remove('is-open');
    menu.classList.remove('is-open');
    btn.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('menu-open');
  }
  function openMenu() {
    btn.classList.add('is-open');
    menu.classList.add('is-open');
    btn.setAttribute('aria-expanded', 'true');
    document.body.classList.add('menu-open');
  }

  btn.addEventListener('click', function () {
    if (menu.classList.contains('is-open')) { closeMenu(); } else { openMenu(); }
  });

  Array.prototype.forEach.call(menu.querySelectorAll('a'), function (link) {
    link.addEventListener('click', closeMenu);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeMenu();
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth > 900) closeMenu();
  });
})();

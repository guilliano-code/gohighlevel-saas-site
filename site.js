/* FLOWSA — shared behaviour for all pages built by tools/build_site.py */

/* ── Mobile menu ─────────────────────────────────── */
(function () {
  var btn = document.getElementById('burger');
  var menu = document.getElementById('mobile-menu');
  if (!btn || !menu) return;
  btn.addEventListener('click', function () {
    var open = menu.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  menu.addEventListener('click', function (e) {
    if (e.target.tagName === 'A') { menu.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }
  });
})();

/* ── Nav dropdowns (click for touch & keyboard; hover handled in CSS) ── */
(function () {
  var dds = document.querySelectorAll('.dd');
  function closeAll(except) {
    dds.forEach(function (d) {
      if (d === except) return;
      d.classList.remove('open');
      d.querySelector('.dd-btn').setAttribute('aria-expanded', 'false');
    });
  }
  dds.forEach(function (d) {
    var b = d.querySelector('.dd-btn');
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = d.classList.toggle('open');
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
      closeAll(d);
    });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.dd')) closeAll(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeAll(); });
})();

/* ── Results sliders ─────────────────────────────── */
document.querySelectorAll('.slider').forEach(function (slider) {
  var track = slider.querySelector('.slider-track');
  var prev = slider.querySelector('.slider-prev');
  var next = slider.querySelector('.slider-next');
  function step() { var s = track.querySelector('.slide'); return s.offsetWidth + 32; }
  function update() {
    prev.disabled = track.scrollLeft < 4;
    next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 4;
  }
  prev.addEventListener('click', function () { track.scrollBy({ left: -step() }); });
  next.addEventListener('click', function () { track.scrollBy({ left: step() }); });
  track.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  update();
});

/* ── Accordions: one open at a time per list ─────── */
document.querySelectorAll('.faq-list, .incl-grid > div').forEach(function (list) {
  var items = list.querySelectorAll('details');
  items.forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (!d.open) return;
      items.forEach(function (o) { if (o !== d) o.open = false; });
    });
  });
});

/* ── Reveal on scroll ────────────────────────────── */
(function () {
  var els = document.querySelectorAll('.rv');
  if (!('IntersectionObserver' in window)) { els.forEach(function (el) { el.classList.add('in'); }); return; }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
  }, { rootMargin: '0px 0px -8% 0px' });
  els.forEach(function (el) { io.observe(el); });
})();

/* ── Billing toggle (prijzen) ────────────────────── */
(function () {
  var opts = document.querySelectorAll('.bill-opt');
  var sw = document.querySelector('.bill-switch');
  if (!opts.length) return;
  var mode = 'yearly';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function countTo(el, to) {
    var from = parseInt(el.textContent, 10) || 0;
    if (reduce || from === to) { el.textContent = to; return; }
    var start = performance.now(), dur = 480;
    (function tick(now) {
      var t = Math.min((now - start) / dur, 1);
      var eased = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.round(from + (to - from) * eased);
      if (t < 1) requestAnimationFrame(tick);
    })(start);
  }
  function set(m) {
    if (m === mode) return;
    mode = m;
    opts.forEach(function (o) {
      var on = o.dataset.bill === m;
      o.classList.toggle('is-on', on);
      o.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    sw.classList.toggle('is-monthly', m === 'monthly');
    document.querySelectorAll('.js-price').forEach(function (el) { countTo(el, parseInt(el.dataset[m], 10)); });
    document.querySelectorAll('.js-note').forEach(function (el) { el.textContent = el.dataset[m]; });
  }
  opts.forEach(function (o) { o.addEventListener('click', function () { set(o.dataset.bill); }); });
  sw.addEventListener('click', function () { set(mode === 'yearly' ? 'monthly' : 'yearly'); });
})();

/* ── Form validation ─────────────────────────────── */
function validateForm(form) {
  var first = null;
  form.querySelectorAll('[required]').forEach(function (el) {
    var msg = '';
    var val = el.value.trim();
    if (el.offsetParent !== null) { /* skip hidden fields */
      if (!val) msg = el.tagName === 'SELECT' ? 'Maak een keuze.' : 'Dit veld is verplicht.';
      else if (el.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(val)) msg = 'Vul een geldig e-mailadres in.';
      else if (el.type === 'tel' && val.replace(/\D/g, '').length < 8) msg = 'Vul een geldig telefoonnummer in.';
    }
    setFieldError(el, msg);
    if (msg && !first) first = el;
  });
  if (first) first.focus();
  return !first;
}

function setFieldError(el, msg) {
  var id = el.id + '-error';
  var err = document.getElementById(id);
  if (!msg) {
    el.classList.remove('is-invalid');
    el.removeAttribute('aria-invalid');
    if (err) err.remove();
    return;
  }
  if (!err) {
    err = document.createElement('p');
    err.className = 'field-error';
    err.id = id;
    el.insertAdjacentElement('afterend', err);
  }
  err.textContent = msg;
  el.classList.add('is-invalid');
  el.setAttribute('aria-invalid', 'true');
  el.setAttribute('aria-describedby', id);
}

function clearOnEdit(e) {
  if (e.target.classList && e.target.classList.contains('is-invalid') && e.target.value.trim()) setFieldError(e.target, '');
}
document.addEventListener('input', clearOnEdit);
document.addEventListener('change', clearOnEdit);

/* ── Contact form → mailto ───────────────────────── */
(function () {
  var form = document.getElementById('contact-form');
  if (!form) return;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!validateForm(form)) return;
    var v = function (n) { return form.querySelector('[name="' + n + '"]').value.trim(); };
    var subject = encodeURIComponent('Nieuwe aanvraag van ' + v('naam') + ' (' + v('bedrijf') + ')');
    var body = encodeURIComponent('Naam: ' + v('naam') + '\nBedrijf: ' + v('bedrijf') + '\nTelefoon: ' + v('telefoon') + '\nE-mail: ' + v('email') + '\n\nBericht:\n' + v('bericht'));
    window.location.href = 'mailto:Guilliano@dailyshotsmedia.com?subject=' + subject + '&body=' + body;
    document.getElementById('contact-success').hidden = false;
    form.reset();
  });
})();

/* ── Call page: blurred VSL, unlocked by a small popup quiz ── */
(function () {
  var overlay = document.getElementById('quiz');
  var form = document.getElementById('quiz-form');
  var wrap = document.getElementById('call-video-wrap');
  if (!overlay || !form || !wrap) return;

  // Lead webhook (GoHighLevel). Leave the placeholder to skip sending.
  var WEBHOOK = 'https://hooks.gohighlevel.com/YOUR_WEBHOOK_URL';
  var STORE = 'flowsaCallLead';

  var video = document.getElementById('call-video');
  var cta = document.getElementById('call-cta');
  var book = document.getElementById('call-book');
  var steps = form.querySelectorAll('.q-step');
  var back = document.getElementById('quiz-back');
  var bar = document.getElementById('quiz-bar');
  var pct = document.getElementById('quiz-pct');
  var answers = {};
  var idx = 0;
  var lastFocus = null;

  function progress(p) {
    bar.style.transform = 'scaleX(' + (p / 100) + ')';
    pct.textContent = p + '%';
    bar.parentElement.setAttribute('aria-valuenow', p);
  }
  // Opens at 50% (like the reference funnel) and fills up per answered step.
  function show(i) {
    idx = i;
    steps.forEach(function (s, n) { s.classList.toggle('is-on', n === i); });
    progress(Math.round(50 + i * 50 / steps.length));
    back.hidden = i === 0;
    var first = steps[i].querySelector('input, button');
    if (first) first.focus({ preventScroll: true });
  }
  function open() {
    if (!wrap.classList.contains('is-locked')) return;
    lastFocus = document.activeElement;
    overlay.hidden = false;
    document.body.classList.add('quiz-open');
    show(idx);
  }
  function close() {
    overlay.hidden = true;
    document.body.classList.remove('quiz-open');
    if (lastFocus) lastFocus.focus();
  }
  function bookingLink(data) {
    var q = new URLSearchParams();
    Object.keys(data).forEach(function (k) { if (data[k]) q.set(k, data[k]); });
    return '/demo/?' + q.toString();
  }
  function unlock(data, autoplay) {
    wrap.classList.remove('is-locked');
    video.controls = true;
    cta.hidden = true;
    book.hidden = false;
    book.href = bookingLink(data);
    if (autoplay) { video.play().catch(function () {}); }
  }

  document.querySelectorAll('[data-open-quiz]').forEach(function (b) { b.addEventListener('click', open); });
  overlay.querySelector('[data-close-quiz]').addEventListener('click', close);
  overlay.addEventListener('click', function (e) { if (e.target === overlay) close(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !overlay.hidden) close(); });
  back.addEventListener('click', function () { if (idx > 0) show(idx - 1); });

  // Choice steps: pick an answer and move on.
  form.querySelectorAll('.q-opt').forEach(function (b) {
    b.addEventListener('click', function () {
      var step = b.closest('.q-step');
      step.querySelectorAll('.q-opt').forEach(function (o) { o.classList.remove('is-picked'); });
      b.classList.add('is-picked');
      answers[step.dataset.name] = b.dataset.value;
      setTimeout(function () { show(idx + 1); }, 180);
    });
  });

  // Field steps: validate just this step, Enter moves on.
  form.querySelectorAll('.q-field .q-next[type="button"]').forEach(function (b) {
    b.addEventListener('click', function () {
      var step = b.closest('.q-step');
      if (validateForm(step)) show(idx + 1);
    });
  });
  form.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter' || e.target.tagName !== 'INPUT') return;
    var next = steps[idx].querySelector('.q-next[type="button"]');
    if (next) { e.preventDefault(); next.click(); }
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!validateForm(steps[idx])) return;
    ['telefoon', 'email', 'naam'].forEach(function (n) { answers[n] = form.querySelector('[name="' + n + '"]').value.trim(); });
    progress(100);
    if (WEBHOOK.indexOf('YOUR_WEBHOOK_URL') === -1) {
      var payload = Object.assign({ bron: 'flowsa-callpagina' }, answers);
      fetch(WEBHOOK, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }).catch(function () {});
    }
    try { localStorage.setItem(STORE, JSON.stringify({ naam: answers.naam, email: answers.email, telefoon: answers.telefoon })); } catch (err) {}
    setTimeout(function () { close(); unlock(answers, true); }, 250);
  });

  // Returning visitor who already filled it in: video stays unlocked.
  try {
    var saved = JSON.parse(localStorage.getItem(STORE) || 'null');
    if (saved && saved.email) unlock(saved, false);
  } catch (err) {}
})();

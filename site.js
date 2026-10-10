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
  function set(m) {
    mode = m;
    opts.forEach(function (o) {
      var on = o.dataset.bill === m;
      o.classList.toggle('is-on', on);
      o.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    sw.classList.toggle('is-monthly', m === 'monthly');
    document.querySelectorAll('.js-price, .js-note').forEach(function (el) { el.textContent = el.dataset[m]; });
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

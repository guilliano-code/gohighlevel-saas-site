#!/usr/bin/env node
/*
 * Fetch candidate photos per trade from Unsplash (free-license filter only).
 *
 *   node tools/fetch_trade_photos.js <outdir> [n=4]
 *
 * Writes <outdir>/<slug>-<i>.jpg (640px wide) and <outdir>/candidates.json
 * with the Unsplash photo page + photographer for each candidate, so a human
 * (or the agent) can pick one per trade and copy it into img/vakgebieden/.
 *
 * Needs puppeteer-core and a local Chrome (Unsplash blocks plain curl on its API).
 * Unsplash License: free for commercial use, no attribution required.
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require(process.env.PUPPETEER_PATH || 'puppeteer-core');

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const TRADES = [
  ['hoveniers', 'gardener landscaping'],
  ['verbouwingen', 'home renovation worker'],
  ['hogedrukreiniging', 'pressure washing'],
  ['hondentrimsalons', 'dog groomer'],
  ['verhuisbedrijven', 'movers moving boxes'],
  ['vloer-tapijtreiniging', 'carpet cleaning'],
  ['dakdekkers', 'roofer'],
  ['klimaattechniek', 'air conditioner repair'],
  ['loodgieters', 'plumber'],
  ['elektriciens', 'electrician'],
  ['klusbedrijven', 'handyman tools'],
  ['schilders', 'house painter'],
  ['terrassen-vlonders', 'wooden deck patio'],
  ['gevelbekleding', 'house siding'],
  ['zwembadbouw', 'swimming pool backyard'],
  ['bestrating', 'paving stones'],
  ['tuinaanleg', 'stone patio hardscape'],
  ['kozijnen-deuren', 'window installation'],
  ['aannemers', 'construction worker'],
  ['ongediertebestrijding', 'pest control'],
  ['boomverzorging', 'chainsaw tree cutting'],
];

(async () => {
  const out = process.argv[2];
  const n = +(process.argv[3] || 4);
  const only = process.argv[4] ? process.argv[4].split(',') : null;
  fs.mkdirSync(out, { recursive: true });
  const b = await puppeteer.launch({ executablePath: CHROME, headless: 'new' });
  const pg = await b.newPage();
  await pg.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36');
  const manifestPath = path.join(out, 'candidates.json');
  const manifest = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath)) : {};
  for (const [slug, q] of TRADES) {
    if (only && !only.includes(slug)) continue;
    await pg.goto('https://unsplash.com/s/photos/' + encodeURIComponent(q.replace(/ /g, '-')) + '?license=free', { waitUntil: 'networkidle2', timeout: 60000 });
    const found = await pg.evaluate((n) => {
      const res = [];
      document.querySelectorAll('figure').forEach((fig) => {
        if (res.length >= n) return;
        const a = fig.querySelector('a[href^="/photos/"]');
        const img = fig.querySelector('img[srcset*="images.unsplash.com/photo-"]');
        const by = fig.querySelector('a[href^="/@"]');
        if (!a || !img) return;
        const src = (img.getAttribute('srcset') || '').split(',')[0].trim().split(' ')[0];
        res.push({ page: 'https://unsplash.com' + a.getAttribute('href'), base: src.split('?')[0], by: by ? by.textContent.trim() : '' });
      });
      return res;
    }, n);
    manifest[slug] = [];
    for (let i = 0; i < found.length; i++) {
      const url = found[i].base + '?w=640&h=400&fit=crop&q=75&fm=jpg';
      const r = await fetch(url);
      if (!r.ok) continue;
      fs.writeFileSync(path.join(out, `${slug}-${i}.jpg`), Buffer.from(await r.arrayBuffer()));
      manifest[slug].push({ file: `${slug}-${i}.jpg`, ...found[i] });
    }
    console.log(slug, manifest[slug].length);
  }
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
  await b.close();
})();

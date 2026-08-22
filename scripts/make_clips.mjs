/* Clip factory: records vertical gameplay videos of the three games
   with scripted "good player" runs, then muxes in each game's real
   generated soundtrack and a caption via ffmpeg.

   Output: dist/clips/<game>-<variant>.mp4  (720x1280, ~25-30s)

   Requires: node + playwright (chromium at /opt/pw-browsers/chromium),
   ffmpeg, python3 (scripts/clip_music.py).

     node scripts/make_clips.mjs [tower|drop|beat]   (default: all)
*/
import { chromium } from 'playwright';
import { createServer } from 'http';
import { readFileSync, existsSync, mkdirSync, readdirSync, renameSync } from 'fs';
import { join, extname, dirname } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(ROOT, 'dist', 'clips');
mkdirSync(OUT, { recursive: true });
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png' };

function serve(root, port) {
  const srv = createServer((req, res) => {
    const p = join(root, req.url === '/' ? 'index.html' : req.url.split('?')[0]);
    if (!existsSync(p)) { res.writeHead(404); return res.end('x'); }
    res.writeHead(200, { 'content-type': MIME[extname(p)] || 'application/octet-stream' });
    res.end(readFileSync(p));
  });
  return new Promise(r => srv.listen(port, () => r(srv)));
}

const W = 720, H = 1280;

async function record(gameDir, port, caption, song, secs, drive) {
  const srv = await serve(join(ROOT, gameDir), port);
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await browser.newContext({
    viewport: { width: W, height: H },
    recordVideo: { dir: OUT, size: { width: W, height: H } },
  });
  const page = await ctx.newPage();
  await page.goto(`http://localhost:${port}/`);
  await page.waitForTimeout(1200);
  await drive(page);
  await ctx.close();           // flushes the webm
  await browser.close();
  srv.close();
  // newest webm in OUT is ours
  const webm = readdirSync(OUT).filter(f => f.endsWith('.webm'))
    .map(f => join(OUT, f)).sort((a, b) => 0)[0];
  const raw = join(OUT, `${song}-raw.webm`);
  renameSync(webm, raw);
  const wav = join(OUT, `${song}.wav`);
  execSync(`python3 ${join(ROOT, 'scripts', 'clip_music.py')} ${song} ${secs} ${wav}`);
  const mp4 = join(OUT, `${song}.mp4`);
  const drawtext = caption
    ? `,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='${caption}':fontcolor=white:fontsize=44:borderw=3:bordercolor=black@0.6:x=(w-text_w)/2:y=110`
    : '';
  execSync(`ffmpeg -y -i ${raw} -i ${wav} -t ${secs} -vf "scale=${W}:${H}${drawtext}" ` +
    `-c:v libx264 -pix_fmt yuv420p -r 30 -preset veryfast -crf 26 -c:a aac -b:a 128k -shortest ${mp4} 2>/dev/null`);
  execSync(`rm -f ${raw} ${wav}`);
  console.log('clip:', mp4);
}

// ---- scripted runs ------------------------------------------------------

async function driveTower(page) {
  // perfect-stack showcase with one dramatic slice recovery
  for (let i = 0; i < 16; i++) {
    const off = (i === 6 || i === 11) ? 30 : 0;          // two slices for drama
    await page.evaluate((o) => window.DEV.dropAt(window.DEV.topX() + o), off);
    await page.waitForTimeout(i < 4 ? 1500 : 1250);
  }
}

async function driveDrop(page) {
  // merge cascades, finishing on a moonburst
  const drops = [[210, 0], [210, 0], [210, 1], [210, 1], [150, 2], [150, 2],
                 [300, 3], [300, 3], [210, 4], [210, 4], [210, 5], [210, 5]];
  for (const [x, tier] of drops) {
    await page.evaluate(([xx, tt]) => window.DEV.dropAt(xx, tt), [x, tier]);
    await page.waitForTimeout(1400);
  }
  await page.evaluate(() => { window.DEV.spawn(9, 200, 420, 0); window.DEV.spawn(9, 200, 240, 0); });
  await page.waitForTimeout(3500);
}

async function driveBeat(page) {
  // auto-play the song accurately; miss nothing — fever showcase
  await page.evaluate(() => window.DEV.start());
  await page.evaluate(() => {
    window.__autotap = setInterval(() => {
      const s = window.DEV.state();
      if (s.state !== 'play') return;
      // tap any tile within the perfect window
      const tiles = [];
      for (let l = 0; l < 4; l++) tiles.push(l);
      tiles.forEach(l => window.DEV.tap(l));
    }, 45);
  });
  await page.waitForTimeout(27000);
  await page.evaluate(() => clearInterval(window.__autotap));
}

// ---- main ---------------------------------------------------------------

const which = process.argv[2] || 'all';
if (which === 'tower' || which === 'all') {
  await record('game6', 8961, 'Can you stack higher?', 'tower', 25, driveTower);
}
if (which === 'drop' || which === 'all') {
  await record('game7', 8962, 'Two of a kind = bigger critter', 'drop', 25, driveDrop);
}
if (which === 'beat' || which === 'all') {
  await record('game8', 8963, 'Your taps play the song', 'beat', 25, driveBeat);
}
console.log('done');

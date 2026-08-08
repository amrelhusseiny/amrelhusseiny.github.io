/**
 * Build-time image optimization: converts every local blog/notes image to
 * a ~900px WebP (plus width/height), writes it to public/, and generates a
 * JSON map so the remark plugin can rewrite markdown refs.
 *
 * Run before `astro build` (see package.json "build" script).
 */
import sharp from 'sharp';
import { readdirSync, statSync, mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname, extname } from 'node:path';

const ROOTS = ['public/blog', 'public/notes'];
const EXTS = new Set(['.png', '.jpg', '.jpeg']);
const WIDTH = 900;

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p, out);
    else if (EXTS.has(extname(p).toLowerCase())) out.push(p);
  }
  return out;
}

const map = {};
for (const root of ROOTS) {
  if (!existsSync(root)) continue;
  for (const file of walk(root)) {
    const out = file.replace(/\.[a-z]+$/i, '.webp');
    try {
      const img = sharp(file);
      const meta = await img.metadata();
      const outImg = img
        .resize({ width: Math.min(WIDTH, meta.width || WIDTH), withoutEnlargement: true })
        .webp({ quality: 80 });
      await outImg.toFile(out);
      const outMeta = await sharp(out).metadata();
      // map key is the URL path (strip public/ prefix)
      const urlPath = '/' + out.replace(/^public\//, '');
      map[file.replace(/^public\//, '/')] = {
        webp: urlPath,
        width: outMeta.width,
        height: outMeta.height,
      };
      const before = statSync(file).size;
      const after = statSync(out).size;
      console.log(`  ${file} -> ${out} (${(before/1024).toFixed(0)}KB -> ${(after/1024).toFixed(0)}KB)`);
    } catch (e) {
      console.error(`  SKIP ${file}: ${e.message}`);
    }
  }
}

writeFileSync('public/.imgmap.json', JSON.stringify(map));
console.log(`Wrote ${Object.keys(map).length} optimized images -> public/.imgmap.json`);

/**
 * Rewrites Hugo-style image references so they resolve correctly in Astro.
 *
 * Hugo resolved relative image paths against the page bundle folder
 * (e.g. content/blog/<bundle>/img.png). In Astro, images live in
 * public/ mirrored at /blog/<bundle>/img.png and /notes/<bundle>/img.png.
 *
 * This plugin rewrites relative ![](img.png) refs to absolute
 * /<collection>/<bundle>/img.png, and leaves absolute/http refs alone.
 */
import { visit } from 'unist-util-visit';

const EXTS = /\.(png|jpe?g|gif|webp|svg|avif)(\?.*)?$/i;

export default function remarkImages() {
  return (tree, file) => {
    const id = file?.data?.astro?.frontmatter?.id || file?.data?.astro?.contentCollection;
    const collection = file?.data?.astro?.contentCollection || 'blog';
    const entryId = file?.data?.astro?.id || '';
    const bundle = String(entryId).split('/')[0];
    if (!bundle) return;

    visit(tree, 'image', (node) => {
      if (!node.url || node.url.startsWith('http') || node.url.startsWith('/') || node.url.startsWith('data:')) {
        return;
      }
      if (!EXTS.test(node.url)) return;
      node.url = `/${collection}/${bundle}/${node.url}`;
    });
  };
}

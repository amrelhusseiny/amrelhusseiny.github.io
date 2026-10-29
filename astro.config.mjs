import { defineConfig } from 'astro/config';
import { fileURLToPath } from 'node:url';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import vercel from '@astrojs/vercel';

export default defineConfig({
  site: 'https://amroelhusseini.vercel.app',
  output: 'static',
  adapter: vercel(),
  integrations: [mdx(), sitemap()],
  markdown: {
    remarkPlugins: [fileURLToPath(new URL('./src/lib/remark-optimize-images.mjs', import.meta.url))],
    shikiConfig: {
      themes: {
        light: 'github-light',
        dark: 'github-dark',
      },
      defaultColor: false,
    },
  },
});

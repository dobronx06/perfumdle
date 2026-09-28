import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

const today = new Date().toISOString();

export default defineConfig({
  site: 'https://perfumdle.com',
  output: 'static',
  trailingSlash: 'always',
  build: { format: 'directory' },
  redirects: {
    // The game used to live on the home page; the old list page grew into the catalogue.
    '/fr/liste-150-parfums-perfumdle': '/fr/parfums/',
    '/en/liste-150-parfums-perfumdle': '/en/perfumes/',
  },
  integrations: [
    sitemap({
      filter: (page) => !page.includes('liste-150-parfums-perfumdle'),
      serialize(item) {
        item.lastmod = today;
        const path = new URL(item.url).pathname;
        const depth = path.split('/').filter(Boolean).length;
        item.priority = depth <= 1 ? 1.0 : depth === 2 ? 0.8 : 0.6;
        item.changefreq = path.includes('/jeu/') || path.includes('/game/') ? 'daily' : 'weekly';
        return item;
      },
      i18n: { defaultLocale: 'fr', locales: { fr: 'fr', en: 'en' } },
    }),
  ],
  vite: { build: { assetsInlineLimit: 0 } },
});

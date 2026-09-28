/** JSON-LD builders (schema.org). Keep every page's structured data consistent. */
import { SITE, type Faq } from './catalog';

const abs = (p: string) => (p.startsWith('http') ? p : `${SITE}${p}`);

export function breadcrumbLd(items: { name: string; href?: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((it, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: it.name,
      ...(it.href ? { item: abs(it.href) } : {}),
    })),
  };
}

export function faqLd(items: Faq[]) {
  if (!items.length) return null;
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map((f) => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } })),
  };
}

export function itemListLd(name: string, items: { name: string; href: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name,
    numberOfItems: items.length,
    itemListElement: items.map((it, i) => ({ '@type': 'ListItem', position: i + 1, name: it.name, url: abs(it.href) })),
  };
}

export function articleLd(opts: { headline: string; description: string; path: string; image?: string; lang: string; about?: string }) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: opts.headline,
    description: opts.description,
    inLanguage: opts.lang,
    mainEntityOfPage: abs(opts.path),
    ...(opts.image ? { image: abs(opts.image) } : {}),
    ...(opts.about ? { about: { '@type': 'Thing', name: opts.about } } : {}),
    author: { '@type': 'Organization', name: 'Perfumdle', url: SITE },
    publisher: { '@type': 'Organization', name: 'Perfumdle', url: SITE, logo: { '@type': 'ImageObject', url: `${SITE}/favicon.svg` } },
    dateModified: BUILD_DATE,
  };
}

export const BUILD_DATE = new Date().toISOString().slice(0, 10);

export const compact = <T,>(xs: (T | null | undefined)[]) => xs.filter(Boolean) as T[];

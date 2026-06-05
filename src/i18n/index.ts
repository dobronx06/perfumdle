import fr from './fr.json';
import en from './en.json';

const translations: Record<string, Record<string, string>> = { fr, en };

export type Locale = 'fr' | 'en';
export const locales: Locale[] = ['fr', 'en'];
export const defaultLocale: Locale = 'fr';

export function t(locale: Locale, key: string, params?: Record<string, string>): string {
  let str = translations[locale]?.[key] ?? translations[defaultLocale]?.[key] ?? key;
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      str = str.replaceAll(`{${k}}`, v);
    }
  }
  return str;
}

export function localePath(locale: Locale, path: string = '/'): string {
  return `/${locale}${path === '/' ? '/' : path}`;
}

export function altLocale(locale: Locale): Locale {
  return locale === 'fr' ? 'en' : 'fr';
}

export function ogLocale(locale: Locale): string {
  return locale === 'fr' ? 'fr_FR' : 'en_US';
}

export function dateLocale(locale: Locale): string {
  return locale === 'fr' ? 'fr-FR' : 'en-US';
}

export function getTranslations(locale: Locale): Record<string, string> {
  return translations[locale] ?? translations[defaultLocale];
}

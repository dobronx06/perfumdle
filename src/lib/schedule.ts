/**
 * Drip-feed publishing. Programmatic page families listed in
 * src/data/publish-schedule.json only go live once their date has passed,
 * so Google sees steady growth instead of a sudden spike of URLs.
 * A daily rebuild (see .github/workflows/daily-rebuild.yml) publishes the next batch.
 */
import schedule from '../data/publish-schedule.json';

type Kind = keyof typeof schedule;
// PUBLISH_DATE=YYYY-MM-DD lets you preview the site as it will be on a given day.
const today = process.env.PUBLISH_DATE ?? new Date().toISOString().slice(0, 10);

export function isPublished(kind: Kind, slug: string): boolean {
  const date = (schedule[kind] as Record<string, string>)[slug];
  return !!date && date <= today;
}

export function publishedSlugs(kind: Kind): string[] {
  return Object.entries(schedule[kind] as Record<string, string>).filter(([, d]) => d <= today).map(([s]) => s);
}

/** The build's publishing day (YYYY-MM-DD). */
export const buildDay = today;

/** Slugs whose publish date is exactly the build day: the URLs that appear in this build. */
export function publishedToday(kind: Kind): string[] {
  return Object.entries(schedule[kind] as Record<string, string>).filter(([, d]) => d === today).map(([s]) => s);
}

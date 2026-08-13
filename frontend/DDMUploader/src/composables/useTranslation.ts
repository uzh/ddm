import { useI18n } from 'vue-i18n';

export type CustomTranslations = Record<string, Record<string, unknown>>;

let customMessages: CustomTranslations = {};

/**
 * Stores researcher-supplied translation overrides outside vue-i18n's own
 * message tree. vue-i18n runs in runtime-only mode (see vue.config.js) and
 * has no message compiler, so any message string arriving after build time
 * can't be compiled by vue-i18n itself. useTranslation() below interpolates
 * such overrides directly instead, avoiding the need for a runtime,
 * eval-based compiler.
 */
export function setCustomTranslations(custom: CustomTranslations | undefined): void {
  customMessages = custom || {};
}

function resolvePath(source: Record<string, unknown>, path: string): string | undefined {
  const value = path.split('.').reduce<unknown>((acc, part) => {
    return acc && typeof acc === 'object' ? (acc as Record<string, unknown>)[part] : undefined;
  }, source);
  return typeof value === 'string' ? value : undefined;
}

function interpolate(message: string, params?: Record<string, unknown>): string {
  if (!params) return message;
  return message.replace(/\{(\w+)\}/g, (match, name) =>
    Object.prototype.hasOwnProperty.call(params, name) ? String(params[name]) : match
  );
}

/**
 * Drop-in replacement for vue-i18n's useI18n(): checks custom translation
 * overrides first (interpolating them itself), then falls back to
 * vue-i18n's own (precompiled) t()/te() for the default messages.
 */
export function useTranslation(...args: Parameters<typeof useI18n>) {
  const { t: baseT, te: baseTe, locale } = useI18n(...args);

  function t(key: string, params?: Record<string, unknown>): string {
    const custom = resolvePath(customMessages[locale.value] || {}, key);
    return custom !== undefined ? interpolate(custom, params) : baseT(key, params ?? {});
  }

  function te(key: string): boolean {
    return resolvePath(customMessages[locale.value] || {}, key) !== undefined || baseTe(key);
  }

  return { t, te, locale };
}

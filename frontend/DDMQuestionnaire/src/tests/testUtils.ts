import { createI18n } from 'vue-i18n';
import en from '@questionnaire/locales/en.json';
import de from '@questionnaire/locales/de.json';

export const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: {en, de},
});

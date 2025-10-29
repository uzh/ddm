import { createApp } from 'vue'
import QApp from './components/QuestionnaireApp.vue'
import { onlyDigits, validEmail } from './directives/formDirectives';
import { createI18n } from 'vue-i18n'

import en from './locales/en.json';
import de from './locales/de.json';
import it from './locales/it.json';
import fr from './locales/fr.json';

const APP_CONFIG = {
  selector: '#qapp',
  defaultLocale: 'en',
  fallbackLocale: 'en',
}

const i18n = createI18n({
  legacy: false,
  locale: APP_CONFIG.defaultLocale,
  fallbackLocale: APP_CONFIG.fallbackLocale,
  messages: {
    en,
    de,
    it,
    fr
  }
})

const selector = APP_CONFIG.selector;
const mountEl = document.querySelector(selector) as HTMLElement;
const app = createApp(QApp, {...mountEl.dataset})

// Set i18n locale based on the data attribute.
const userLanguage = mountEl.dataset.language || APP_CONFIG.defaultLocale;
const availableLocales = i18n.global.availableLocales as string[];

if (availableLocales.includes(userLanguage)) {
  i18n.global.locale.value = userLanguage as 'en' | 'de' | 'it' | 'fr';
} else {
  i18n.global.locale.value = APP_CONFIG.fallbackLocale as 'en' | 'de' | 'it' | 'fr';
}

app.directive('only-digits', onlyDigits);
app.directive('valid-email', validEmail);

app.use(i18n)
app.mount(selector)

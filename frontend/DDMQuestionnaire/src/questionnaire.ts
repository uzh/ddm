import { createApp } from 'vue'
import QApp from './components/QuestionnaireApp.vue'
import { onlyDigits, validEmail } from './directives/formDirectives';
import { createI18n } from 'vue-i18n'

import en from './locales/en.json';
import de from './locales/de.json';
import it from './locales/it.json';
import fr from './locales/fr.json';

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en,
    de,
    it,
    fr
  }
})

const selector = "#qapp";
const mountEl = document.querySelector(selector) as HTMLElement;
const app = createApp(QApp, {...mountEl.dataset})

app.directive('only-digits', onlyDigits);
app.directive('valid-email', validEmail);

app.use(i18n)
app.mount(selector)

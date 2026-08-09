import { createApp } from 'vue'
import QApp from './components/QuestionnaireApp.vue'
import { onlyDigits, validEmail, validLength, validValue } from './directives/formDirectives';
import { createI18n } from 'vue-i18n'

import en from './locales/en.json';
import de from './locales/de.json';
import it from './locales/it.json';
import fr from './locales/fr.json';
import type {FilterConfig, QuestionnaireConfig} from "@questionnaire/types/questionnaire";


/**
 * Entry point for the DDM questionnaire Vue application.
 *
 * This module initializes the Vue application by:
 * 1. Setting up i18n internationalization
 * 2. Finding the mount element in the DOM
 * 3. Parsing configuration data from data attributes and JSON script blocks
 * 4. Creating and mounting the Vue application with the appropriate props
 *
 * Expected `data-*` attributes on the mount element:
 * - data-action-url
 * - data-language
 *
 * Expected JSON script blocks located within the mount element:
 *  - #q-config-data: Contains the questionnaire configuration
 *  - #filter-config-data: Contains the filter configuration
 *  - #static-variables-data: Contains the values of static variables
 *
 * @throws {Error} If the mount element is not found or required data attributes are missing
 */
function initializeQuestionnaireApp(): void {
  const APP_CONFIG = {
    selector: '#qapp',
    qConfigId: '#q-config-data',
    filterConfigId: '#filter-config-data',
    staticVariablesId: '#static-variables-data',
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

  /* Load questionnaire config */
  let questionnaireConfig: QuestionnaireConfig;
  try {
    questionnaireConfig = JSON.parse(mountEl.querySelector(APP_CONFIG.qConfigId).textContent);
  } catch (err) {
    console.error("Failed to parse questionnaire configuration:", err);
  }

  /* Load filter config */
  let filterConfig: FilterConfig;
  try {
    filterConfig = JSON.parse(mountEl.querySelector(APP_CONFIG.filterConfigId).textContent);
  } catch (err) {
    console.error("Failed to parse filter configuration:", err);
  }

  /* Load static variables */
  let staticVariables: Record<string, string | number>;
  try {
    staticVariables = JSON.parse(mountEl.querySelector(APP_CONFIG.staticVariablesId).textContent);
  } catch (err) {
    console.error("Failed to parse static variables", err);
  }

  const app = createApp(QApp, {
    questionnaireConfig: questionnaireConfig,
    filterConfig: filterConfig,
    staticVariables: staticVariables,
    actionUrl: mountEl.dataset.actionUrl,
    progressUrl: mountEl.dataset.progressUrl,
    language: mountEl.dataset.language
  });

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
  app.directive('valid-length', validLength);
  app.directive('valid-value', validValue);

  app.use(i18n)
  app.mount(selector)
}

initializeQuestionnaireApp();

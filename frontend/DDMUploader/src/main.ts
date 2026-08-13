import { createApp } from 'vue'
import UApp from './UploaderApp.vue'
import { createI18n } from 'vue-i18n'
import { setCustomTranslations } from './composables/useTranslation'

import en from './locales/en.json';
import de from './locales/de.json';
import it from './locales/it.json';
import fr from './locales/fr.json';
import {UploaderConfig} from "@uploader/types/UploaderConfig";

/**
 * Entry point for the DDM uploader Vue application.
 *
 * This module initializes the Vue application by:
 * 1. Setting up i18n internationalization
 * 2. Finding the mount element in the DOM
 * 3. Parsing configuration data from data attributes and JSON script blocks
 * 4. Creating and mounting the Vue application with the appropriate props
 *
 * Expected `data-*` attributes on the mount element:
 * - data-action-url
 * - data-exception-url
 * - data-language
 * - data-csrf-token
 *
 * Expected JSON script blocks located within the mount element:
 *  - #config-data: Contains the uploader configuration
 *  - #custom-translations: Contains custom translations (optional)
 *
 * @throws {Error} If the mount element is not found or required data attributes are missing
 */
function initializeUploaderApp(): void {
  const APP_CONFIG = {
    selector: '#uapp',
    configId: '#config-data',
    customTranslationsId: '#custom-translations',
    defaultLocale: 'en',
    fallbackLocale: 'en',
  }

  const mountEl = document.querySelector(APP_CONFIG.selector) as HTMLElement;

  if (!mountEl) {
    console.error(`Mount element not found using selector: "${APP_CONFIG.selector}"`);
    throw new Error(`Failed to initialize uploader: Mount element "${APP_CONFIG.selector}" not found`);
  }

  // Validate required attributes.
  const requiredAttributes = ['actionUrl', 'csrfToken', 'exceptionUrl'];
  for (const attr of requiredAttributes) {
    const datasetKey = attr.charAt(0).toLowerCase() + attr.slice(1);
    if (!mountEl.dataset[datasetKey]) {
      throw new Error(`Required attribute data-${attr.replace(/[A-Z]/g, m => `-${m.toLowerCase()}`)} is missing`);
    }
  }

  let uploaderConfigs: UploaderConfig[];
  try {
    uploaderConfigs = JSON.parse(mountEl.querySelector(APP_CONFIG.configId).textContent);
  } catch (err) {
    console.error("Failed to parse uploadConfig:", err);
  }

  const app = createApp(UApp, {
    actionUrl: mountEl.dataset.actionUrl,
    exceptionUrl: mountEl.dataset.exceptionUrl,
    language: mountEl.dataset.language,
    uploaderConfigs: uploaderConfigs,
    csrfToken: mountEl.dataset.csrfToken,
  });

  const i18n = createI18n({
    legacy: false,
    locale: APP_CONFIG.defaultLocale,
    fallbackLocale: APP_CONFIG.fallbackLocale,
    messages: { en, de, it, fr },
  })

  // Load custom translations, if provided. Kept separate from vue-i18n's own
  // message tree since they arrive at runtime and vue-i18n has no compiler
  // available to process them (see composables/useTranslation.ts).
  const translationsEl = mountEl.querySelector(APP_CONFIG.customTranslationsId);
  if (translationsEl?.textContent) {
    try {
      setCustomTranslations(JSON.parse(translationsEl.textContent));
    } catch (err) {
      console.error("Failed to parse custom translations:", err);
    }
  }

  // Set i18n locale based on the data attribute.
  const userLanguage = mountEl.dataset.language || APP_CONFIG.defaultLocale;
  const availableLocales = i18n.global.availableLocales as string[];

  if (availableLocales.includes(userLanguage)) {
    i18n.global.locale.value = userLanguage as 'en' | 'de' | 'it' | 'fr';
  } else {
    i18n.global.locale.value = APP_CONFIG.fallbackLocale as 'en' | 'de' | 'it' | 'fr';
  }

  app.use(i18n);
  app.mount(APP_CONFIG.selector);
}

initializeUploaderApp();

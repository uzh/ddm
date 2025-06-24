import { createApp } from 'vue'
import UApp from './UploaderApp.vue'
import { createI18n } from 'vue-i18n'

import en from './locales/en.json';
import de from './locales/de.json';
import {UploaderConfig} from "@uploader/types/UploaderConfig";

function deepMerge(target, source) {
  const result = { ...target };

  for (const key in source) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      result[key] = deepMerge(result[key] || {}, source[key]);
    } else {
      result[key] = source[key];
    }
  }

  return result;
}

/**
 * Entry point for the DDM uploader Vue application.
 *
 * This module initializes the Vue application by:
 * 1. Setting up i18n internationalization
 * 2. Finding the mount element in the DOM
 * 3. Parsing configuration data from data attributes
 * 4. Creating and mounting the Vue application with the appropriate props
 *
 * Expected `data-*` attributes on the mount element:
 * - data-uploader-configs-as-string
 * - data-action-url
 * - data-exception-url
 * - data-language
 * - data-csrf-token
 * - data-custom-translations
 *
 * @throws {Error} If the mount element is not found or required data attributes are missing
 */
function initializeUploaderApp(): void {
  const APP_CONFIG = {
    selector: '#uapp',
    defaultLocale: 'en',
    fallbackLocale: 'en',
  }

  const mountEl = document.querySelector(APP_CONFIG.selector) as HTMLElement;

  if (!mountEl) {
    console.error(`Mount element not found using selector: "${APP_CONFIG.selector}"`);
    throw new Error(`Failed to initialize uploader: Mount element "${APP_CONFIG.selector}" not found`);
  }

  // Validate required attributes.
  const requiredAttributes = ['actionUrl', 'csrfToken', 'uploaderConfigsAsString', 'exceptionUrl'];
  for (const attr of requiredAttributes) {
    const datasetKey = attr.charAt(0).toLowerCase() + attr.slice(1);
    if (!mountEl.dataset[datasetKey]) {
      throw new Error(`Required attribute data-${attr.replace(/[A-Z]/g, m => `-${m.toLowerCase()}`)} is missing`);
    }
  }

  const rawConfig: string = mountEl.dataset.uploaderConfigsAsString;
  let uploaderConfigs: UploaderConfig[] = [];

  try {
    uploaderConfigs = JSON.parse(rawConfig ?? "[]") as UploaderConfig[];
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

  // Load and add custom translations, if provided.
  let messages = {
    en: en,
    de: de,
  };
  if (mountEl.dataset.customTranslations) {
    const customTranslations = JSON.parse(mountEl.dataset.customTranslations || '{}');
    if (!(customTranslations == null) && !(customTranslations == '')) {
      messages = {
        en: deepMerge(en, customTranslations.en || {}),
        de: deepMerge(de, customTranslations.de || {}),
      };
    }
  }

  const i18n = createI18n({
    legacy: false,
    locale: APP_CONFIG.defaultLocale,
    fallbackLocale: APP_CONFIG.fallbackLocale,
    messages: messages
  })

  // Set i18n locale based on the data attribute.
  const userLanguage = mountEl.dataset.language || APP_CONFIG.defaultLocale;
  const availableLocales = i18n.global.availableLocales as string[];

  if (availableLocales.includes(userLanguage)) {
    i18n.global.locale.value = userLanguage as 'en' | 'de';
  } else {
    i18n.global.locale.value = APP_CONFIG.fallbackLocale as 'en' | 'de';
  }

  app.use(i18n);
  app.mount(APP_CONFIG.selector);
}

initializeUploaderApp();

import { createApp } from 'vue'
import QApp from './QuestionnaireApp.vue'
import { createI18n } from 'vue-i18n'

const i18n = new createI18n({
  fallbackLocale: 'en',
})

const selector = "#qapp";
const mountEl = document.querySelector(selector);
const app = createApp(QApp, {...mountEl.dataset})

app.use(i18n)
app.mount(selector)

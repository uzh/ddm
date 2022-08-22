import { createApp } from 'vue'
import UApp from './UploaderApp.vue'
import { createI18n } from 'vue-i18n'

const i18n = new createI18n({

})

const selector = "#uapp";
const mountEl = document.querySelector(selector);
const app = createApp(UApp, {...mountEl.dataset})

app.use(i18n)
app.mount(selector)

import { createApp } from 'vue'
import UApp from './UploaderApp.vue'

const selector = "#uapp";
const mountEl = document.querySelector(selector);

createApp(UApp, {...mountEl.dataset}).mount(selector)

import { createApp } from 'vue'
import QApp from './QuestionnaireApp.vue'

const selector = "#qapp";
const mountEl = document.querySelector(selector);

createApp(QApp, {...mountEl.dataset}).mount('#qapp')

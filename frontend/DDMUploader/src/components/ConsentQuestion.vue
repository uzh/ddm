<script setup lang="ts">
/**
 * Component ConsentQuestion
 *
 * Displays a consent toggle (Agree/Disagree) for blueprint donations, supporting both single and combined consent modes.
 *
 * Features:
 * - Allows user to agree or disagree with data donation.
 * - Supports updating consent individually per blueprint or globally for all blueprints (combinedConsent).
 * - Emits consent changes to parent via 'consentUpdated' event.
 * - Highlights selected choice visually.
 *
 * Props:
 * - combinedConsent (boolean): If true, sets consent for all blueprints.
 * - blueprintId (number | null): Current blueprint ID (null if combined consent).
 *
 * Emits:
 * - consentUpdated (consent: boolean, blueprintId: number | null): Emits updated consent and blueprint context.
 *
 * Dependencies:
 * - vue-i18n for translations.
 */

import { useI18n } from 'vue-i18n';
import {Ref, ref} from "vue";
const { t, te, locale } = useI18n();

const props = defineProps<{
  combinedConsent: boolean,
  blueprintId: number | null;  // Can be null if combinedConsent is true.
}>();

const consented: Ref<boolean | null> = ref(null);

const emit = defineEmits<{
  (e: 'consentUpdated', consent: boolean, blueprintId: number | null): void;
}>();

/**
 * Updates the consent state and emits the change to the parent component.
 *
 * When combinedConsent is true, this emits with a null blueprintId to indicate
 * the change applies to all blueprints. Otherwise, it emits with the specific
 * blueprintId to update consent for just that blueprint.
 *
 * @param consent - Whether the user has consented (true) or declined (false)
 */
function updateConsent(consent: boolean): void {
  emit('consentUpdated', consent, props.blueprintId);
  consented.value = consent;
}

</script>

<template>

  <div v-if="combinedConsent" class="fs-5 fw-bold pb-2">{{ t('feedback.donation-question') }}</div>
  <div v-else class="fw-bold pb-2">{{ t('feedback.donation-question') }}</div>

  <div class="btn-group" role="group" aria-label="Consent options">
    <input type="radio"
           class="btn-check"
           :id="'donate-agree-' + blueprintId"
           :name="'agreement-' + blueprintId"
           :value="true"
           :aria-checked="consented === true"
           autocomplete="off"
           @change="updateConsent(true)"
           required>
    <label :class="{ 'selected-donate-agree': consented === true }"
           :for="'donate-agree-' + blueprintId"
           class="btn button grey-button donation-btn shadow-none">
      {{ t('feedback.donation-agree') }}
    </label>

    <input type="radio"
           class="btn-check"
           :id="'donate-disagree-' + blueprintId"
           :name="'agreement-' + blueprintId"
           :value="false"
           :aria-checked="consented === false"
           autocomplete="off"
           @change="updateConsent(false)">
    <label :class="{ 'selected-donate-disagree': consented === false }"
           :for="'donate-disagree-' + blueprintId"
           class="btn button grey-button donation-btn shadow-none">
      {{ t('feedback.donation-disagree') }}
    </label>
  </div>

</template>

<style scoped>
.selected-donate-agree {
  background: #069143 !important;
  color: white !important;
  font-weight: 600;
}
.selected-donate-disagree {
  background: #f38896 !important;
  font-weight: 600;
}
.donation-btn {
  width: 120px;
  border: none;
  margin: 5px;
}
</style>
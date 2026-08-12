<script setup lang="ts">
/**
 * Component ConsentQuestion
 *
 * Displays a consent toggle (Agree/Disagree) for blueprint donations, supporting both single and combined consent modes.
 *
 * Features:
 * - Allows user to agree or disagree with data donation.
 * - Supports updating consent individually per blueprint or globally for all blueprints (combinedConsent).
 * - Shows a "with deletion" question wording if the blueprint allows excluding individual entries.
 * - Emits consent changes to parent via 'consentUpdated' event.
 * - Highlights selected choice visually.
 *
 * Props:
 * - combinedConsent (boolean): If true, sets consent for all blueprints.
 * - blueprint (Blueprint | null): The blueprint being consented to (null if combined consent).
 * - blueprintId (number | null): Current blueprint ID (null if combined consent).
 *
 * Emits:
 * - consentUpdated (consent: boolean, blueprintId: number | null): Emits updated consent and blueprint context.
 *
 * Dependencies:
 * - vue-i18n for translations.
 */

import { useI18n } from 'vue-i18n';
import {computed, Ref, ref} from "vue";
import {Blueprint} from "@uploader/types/Blueprint";
const { t, te, locale } = useI18n();  // eslint-disable-line @typescript-eslint/no-unused-vars

const props = defineProps<{
  combinedConsent: boolean,
  blueprint: Blueprint | null,
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


/**
 * Whether the exclusion of individual entries is allowed and thus the
 * respective label should be shown.
 */
const isExclusionAllowed = computed(() => {
  if (props.blueprint === null) {
    return false;
  }
  return !!props.blueprint.nested_entry_exclusion_allowed
});

</script>

<template>
  <div
    class="consent-container"
    :class="{ 'consent-container-single': !combinedConsent }"
  >
    <div
      class="consent-question"
    >
      <template v-if="combinedConsent">
        <span v-if="!isExclusionAllowed">{{ t('feedback.donation-question-combined') }}</span>
        <span v-else>{{ t('feedback.donation-question-with-deletion') }}</span>
      </template>
      <template v-else>
        <span v-if="!isExclusionAllowed">{{ t('feedback.donation-question') }}</span>
        <span v-else>{{ t('feedback.donation-question-with-deletion') }}</span>
      </template>
    </div>

    <div
      class="btn-group"
      role="group"
      aria-label="Consent options"
    >
      <input
        :id="'donate-agree-' + blueprintId"
        type="radio"
        class="btn-check"
        :name="'agreement-' + blueprintId"
        :value="true"
        :aria-checked="consented === true"
        autocomplete="off"
        required
        @change="updateConsent(true)"
      >
      <label
        :class="{ 'selected-donate-agree': consented === true }"
        :for="'donate-agree-' + blueprintId"
        class="btn button grey-button donation-btn shadow-none"
      >
        {{ t('feedback.donation-agree') }}
      </label>

      <input
        :id="'donate-disagree-' + blueprintId"
        type="radio"
        class="btn-check"
        :name="'agreement-' + blueprintId"
        :value="false"
        :aria-checked="consented === false"
        autocomplete="off"
        @change="updateConsent(false)"
      >
      <label
        :class="{ 'selected-donate-disagree': consented === false }"
        :for="'donate-disagree-' + blueprintId"
        class="btn button grey-button donation-btn shadow-none"
      >
        {{ t('feedback.donation-disagree') }}
      </label>
    </div>
  </div>
</template>

<style scoped>
.consent-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.consent-container-single {
  padding-left: 25px;
}

.consent-question {
  padding-right: 15px;
  font-weight: 500;
}

.selected-donate-agree {
  background: var(--ddm-consent-agree) !important;
  color: white !important;
  font-weight: 500;
}
.selected-donate-disagree {
  background: var(--ddm-consent-disagree) !important;
  color: white !important;
  font-weight: 500;
}
.donation-btn {
  width: 80px;
  border: none;
  margin: 5px;
}
</style>

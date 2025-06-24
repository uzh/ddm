<script setup lang="ts">
/**
 * Component: ExtractionItem
 *
 * A presentational component that displays extraction results for a single blueprint.
 * It handles different extraction states (pending, success, failure, no data)
 * and provides appropriate UI for each state.
 *
 * Features:
 * - Displays blueprint name and description
 * - Shows state-specific icons (success checkmark, failure X, etc.)
 * - Renders extracted data tables for successful extractions
 * - Displays error messages with expandable technical details
 * - Provides consent controls for successful extractions (when not using combined consent)
 * - Uses computed properties for conditional rendering logic
 *
 * Props:
 * - blueprint (Blueprint): The blueprint configuration object
 * - extractionState (ExtractionStates): Current extraction state for this blueprint
 * - extractionMessage (string): i18n key for state-specific messages
 * - extractionErrorText (string): Formatted error description
 * - extractionOutcome (BlueprintExtractionOutcome): Data extracted from this blueprint
 * - hasDetailErrors (boolean): Whether detailed error information is available
 * - errors (ProcessingError[]): Array of error objects with details
 * - combinedConsent (boolean): Whether consent is managed globally or per-blueprint
 *
 * Emits:
 * - consentUpdated (consent: boolean, blueprintId: number | null): Forwards consent updates
 *   from the ConsentQuestion component
 *
 * Dependencies:
 * - ExtractionTable: For displaying extracted data
 * - ConsentQuestion: For handling consent input
 * - vue-i18n: For translation
 *
 * Note:
 * This component is designed to be a child of ExtractionOverview, receiving preprocessed
 * data and focusing solely on presentation concerns.
 */

import {ExtractionStates} from "@uploader/types/ExtractionStates";
import {Blueprint} from "@uploader/types/Blueprint";
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";
import {ProcessingError} from "@uploader/types/ProcessingError";
import {EXTRACTION_STATES} from "@uploader/utils/stateCatalog";
import ExtractionTable from "@uploader/components/ExtractionTable.vue";
import ConsentQuestion from "@uploader/components/ConsentQuestion.vue";
import {computed} from "vue";
import {useI18n} from "vue-i18n";

const { t, te, locale } = useI18n();

const props = defineProps<{
  blueprint: Blueprint,
  extractionState: ExtractionStates,
  extractionMessage: string | null,
  extractionErrorText: string | null,
  extractionOutcome: BlueprintExtractionOutcome,
  hasDetailErrors: boolean,
  errors: ProcessingError[],
  combinedConsent: boolean
}>();

const emit = defineEmits<{
  (e: 'consentUpdated', consent: boolean, blueprintId: number | null): void;
}>();

const iconStateMap: Record<ExtractionStates, string> = {
  [EXTRACTION_STATES.SUCCESS]: 'bi bi-file-earmark-check-fill text-success',
  [EXTRACTION_STATES.FAILED]: 'bi bi-file-earmark-x-fill text-danger',
  [EXTRACTION_STATES.NO_DATA]: 'bi bi-file-earmark-x-fill text-grey',
  [EXTRACTION_STATES.PENDING]: 'bi bi-file-earmark-fill text-grey',
  [EXTRACTION_STATES.PARTIAL]: ''
};

/**
 * Computes the icon class based on the current extraction state.
 *
 * @returns The Bootstrap icon class string for the current state
 */
const iconClass = computed(() =>
  props.extractionState ? iconStateMap[props.extractionState] : iconStateMap[EXTRACTION_STATES.PENDING]
);

const extractionPending = computed(() => props.extractionState == EXTRACTION_STATES.PENDING);
const extractionSuccess = computed(() => props.extractionState == EXTRACTION_STATES.SUCCESS);
const nothingExtracted = computed(() => props.extractionState == EXTRACTION_STATES.NO_DATA);
const extractionFailed = computed(() => props.extractionState == EXTRACTION_STATES.FAILED);

/**
 * Forwards consent updates from child components to the parent.
 *
 * This method acts as a mediator between ConsentQuestion components
 * and the parent component, preserving the event structure.
 *
 * @param consent - Whether the user has given consent
 * @param blueprintId - ID of the blueprint being consented to, or null for combined consent
 */
const passConsentUpdateToParent = (consent: boolean, blueprintId: number | null): void => {
  emit('consentUpdated', consent, blueprintId);
}
</script>

<template>
  <div class="d-flex flex-column align-items-start pt-3 pb-3 blueprint-row">

    <div class="d-flex flex-row align-items-start pb-1">
      <div class="status-icon"><i :class="iconClass"></i></div>
      <div class="fw-bold">{{ blueprint.name }}</div>
    </div>

    <div class="d-flex flex-row align-items-start w-100 overflow-hidden">
      <div class="status-icon opacity-0"><i :class="iconClass"></i></div>

      <div class="d-flex flex-column w-100">

        <!-- Pending -->
        <template v-if="extractionPending">
          <div>{{ blueprint.description }}</div>
        </template>

        <!-- Success -->
        <template v-else-if="extractionSuccess">
          <div class="pb-3">{{ blueprint.description }}</div>
          <div>
            <ExtractionTable
                :blueprint-outcome="extractionOutcome"
            />
          </div>

          <div v-if="combinedConsent === false" class="pt-3 pb-1">
            <ConsentQuestion
                :combined-consent="combinedConsent"
                :blueprint-id="blueprint.id"
                @consentUpdated="passConsentUpdateToParent"
            />
          </div>

        </template>

        <!-- Nothing extracted -->
        <template v-else-if="nothingExtracted">
          <div class="pb-2">{{ blueprint.description }}</div>
          <div>{{ t(`${extractionMessage}`) }}</div>
        </template>

        <!-- Failed -->
        <template v-else-if="extractionFailed">
          <div>
            {{ t(`${extractionMessage}`) }}
            {{ extractionErrorText }}
          </div>

          <div v-if="hasDetailErrors">
            <details>
              <summary role="button" aria-expanded="false" id="error-details-summary">
                {{ t('feedback.show-error-details') }}
              </summary>
              <div role="region" aria-labelledby="error-details-summary">
                <template v-for="(error, i) in errors" :key="i">
                  <p v-if="te(`${error.i18nDetail}-detail`)">{{ t(`${error.i18nDetail}-detail`, error.context) }}</p>
                </template>
              </div>
            </details>
          </div>
        </template>
      </div>
    </div>

  </div>
</template>

<style scoped>
.text-grey {
  color: #d0d0d0;
}
.status-icon {
  padding-right: 10px;
}
.blueprint-row {
  padding-top: .5rem;
  padding-bottom: .5rem;
  border-top: 1px solid #dee2e6;
}
details {
  background-color: #fbfbfc;
  border-radius: 5px;
  padding: 2px 10px;
  margin-top: 5px;
  font-size: 0.9rem;
  width: 100%;
  color: #3d3d3d;
}
summary {
  font-weight: bold;
  padding-bottom: 5px;
}
</style>
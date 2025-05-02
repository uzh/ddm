<script setup lang="ts">
/**
 * Component: ExtractionOverview
 *
 * This component coordinates the display of extraction results for multiple blueprints.
 * It manages the state of extraction results and delegates rendering to ExtractionItem components.
 *
 * Features:
 * - Dynamic intro message based on overall extraction state
 * - Processes and prepares extraction data for display
 * - Delegates rendering of individual blueprint results to ExtractionItem components
 * - Handles consent updates from child components
 * - Supports reactivity and updates dynamically with extraction state changes
 * - Internationalization (i18n) support for all user-facing text
 *
 * Props:
 * - uploaderState (UploaderStates): Current state of the uploader component
 * - extractionState (ExtractionStates): Overall extraction state
 * - blueprints (Blueprint[]): List of blueprint configurations
 * - blueprintExtractionStates (BlueprintExtractionStates): Extraction states for each blueprint
 * - blueprintOutcomeMap (Record<number, BlueprintExtractionOutcome>): Extraction data for each blueprint
 * - combinedConsent (boolean): Whether consent is managed globally or per blueprint
 *
 * Emits:
 * - consentUpdated (consent: boolean, blueprintId: number | null): Forwards consent updates from ExtractionItem components
 *
 * Internal Utilities:
 * - getBlueprintUIMap(): Creates a data structure with UI display information for each blueprint
 * - updateBlueprintUIMap(): Updates the reactive UI map when extraction states change
 * - getErrorDescription(): Formats user-friendly error descriptions
 * - passConsentUpdateToParent(): Forwards consent events to parent components
 *
 * Dependencies:
 * - ExtractionItem.vue: Renders individual blueprint extraction results
 * - vue-i18n: For dynamic translation and localization
 *
 * Architecture:
 * This component follows a container/presentational pattern where ExtractionOverview
 * manages state and coordinates, while ExtractionItem handles presentation details.
 */

import {computed, onMounted, reactive, watch} from 'vue';
import { useI18n } from 'vue-i18n';
import {EXTRACTION_STATES} from "@uploader/utils/stateCatalog";
import {BlueprintExtractionStates, ExtractionStates} from "@uploader/types/extractionStates";
import {BlueprintExtractionOutcome} from "@uploader/classes/blueprintExtractionOutcome";
import {UploaderStates} from "@uploader/types/UploaderState";
import {Blueprint} from "@uploader/types/Blueprint";
import {ProcessingError} from "@uploader/types/ProcessingError";
import ExtractionItem from "@uploader/components/ExtractionItem.vue";

const { t, te, locale } = useI18n();

const props = defineProps<{
  uploaderState: UploaderStates,
  extractionState: ExtractionStates,
  blueprints: Blueprint[],
  blueprintExtractionStates: BlueprintExtractionStates,
  blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>,
  combinedConsent: boolean
}>();

const emit = defineEmits<{
  (e: 'consentUpdated', consent: boolean, blueprintId: number | null): void;
}>();

interface BlueprintUIData {
  state: ExtractionStates;
  msg: string;
  errors: ProcessingError[];
  anyDetails: boolean;
  errorText: string;
}

const blueprintUIMap: Record<number, BlueprintUIData> = reactive(getBlueprintUIMap()); // Map containing blueprint information used in the UI.

onMounted(() => {
  updateBlueprintUIMap()
});

/**
 * Updates the blueprint UI map when the extractionState changes.
 */
watch(
  () => props.uploaderState,
  () => {
    if (props.extractionState != EXTRACTION_STATES.PENDING) {
      updateBlueprintUIMap();
    }
  },
  { immediate: true, deep: true }
);

/**
 * Creates the blueprint UI map based on the current blueprintExtractionStates
 * and the current blueprintOutcomeMap.
 */
function getBlueprintUIMap(): Record<number, BlueprintUIData> {
  return Object.fromEntries(props.blueprints.map(bp => {
    const state = props.blueprintExtractionStates[bp.id]?.state;
    const msg = props.blueprintExtractionStates[bp.id]?.i18nState;
    const errors = props.blueprintOutcomeMap[bp.id]?.processingErrors ?? [];
    const anyDetails = errors.some(e => te(`${e.i18nDetail}-detail`));
    const errorText = getErrorDescription(errors);

    return [bp.id, {
      state,
      msg,
      errors,
      anyDetails,
      errorText
    }];
  }))
}

/**
 * Updates the reactive blueprint UI map with current extraction state data.
 *
 * This method maintains reactivity by clearing and reassigning properties
 * of the existing reactive object rather than replacing it entirely.
 * It should be called whenever underlying extraction states change.
 */
function updateBlueprintUIMap(): void {
  const newMap = getBlueprintUIMap();
  // Replace the properties of the reactive object to maintain reactivity
  Object.keys(blueprintUIMap).forEach(key => delete blueprintUIMap[key]);
  Object.assign(blueprintUIMap, newMap);
}

/**
 * Generates a human-readable description of processing errors.
 *
 * If there are no errors, an empty string is returned.
 * If there is one error, its localized detail is returned.
 * If there are multiple errors, a comma-separated list of their
 * lowercased localized details is returned, with "and" before the last error.
 *
 * @param errors An array of `ProcessingError` objects. Each object is expected
 * to have `i18nDetail` (the i18n key for the error message) and
 * `context` (optional context object for i18n).
 * @returns A string describing the errors.
 */
function getErrorDescription(errors: ProcessingError[]): string {
  let errorDescription: string = '';
  if (errors.length === 0) {
    return '';
  } else if (errors.length === 1) {
    return t(`${errors[0].i18nDetail}`, errors[0].context);
  } else {
    for (let i = 0; i < errors.length; i++) {
      errorDescription += t(`${errors[i].i18nDetail}`, errors[i].context).toLowerCase();
      if (i < errors.length - 2) {
        errorDescription += ', ';
      } else if (i === errors.length - 2) {
        errorDescription += ', and ';
      }
    }
  }
  return errorDescription;
}

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

const introText = computed(() =>
  props.extractionState === EXTRACTION_STATES.PENDING
    ? t("feedback.intro-extraction-pending")
    : t('feedback.intro-extraction-complete')
);
</script>

<template>
  <!-- Intro -->
  <div class="pb-3 d-flex align-items-center">
    <span class="section-icon"><i class="bi bi-file-earmark-text"></i></span>
    <span class="section-heading">{{ introText }}</span>
  </div>

  <!-- Blueprint overview -->
  <ExtractionItem
    v-for="blueprint in props.blueprints"
    :key="blueprint.id"
    :blueprint="blueprint"
    :extraction-state="blueprintUIMap[blueprint.id]?.state"
    :extraction-message="blueprintUIMap[blueprint.id]?.msg"
    :extraction-error-text="blueprintUIMap[blueprint.id]?.errorText"
    :extraction-outcome="blueprintOutcomeMap[blueprint.id]"
    :has-detail-errors="blueprintUIMap[blueprint.id].anyDetails"
    :errors="blueprintUIMap[blueprint.id]?.errors || []"
    :combined-consent="combinedConsent"
    @consent-updated="passConsentUpdateToParent"
  />
</template>

<style scoped>

</style>

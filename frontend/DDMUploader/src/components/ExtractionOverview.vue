<script setup lang="ts">
/**
 * Component: ExtractionOverview
 *
 * Coordinates the display of extraction results for all of an uploader's
 * (primary, non-backup) blueprints, delegating each one to ExtractionItem.
 * If a primary blueprint's extraction failed but one of its backups
 * succeeded, the successful backup is rendered in its place; backups are
 * otherwise never shown on their own. Successfully-extracted blueprints are
 * listed first; the rest are grouped in a collapsible section below.
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
 */

import {computed, onMounted, reactive, ref, watch} from 'vue';
import { useI18n } from 'vue-i18n';
import {EXTRACTION_STATES} from "@uploader/utils/stateCatalog";
import {BlueprintExtractionStates, ExtractionStates} from "@uploader/types/ExtractionStates";
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";
import {UploaderStates} from "@uploader/types/UploaderState";
import {Blueprint} from "@uploader/types/Blueprint";
import {ProcessingError} from "@uploader/types/ProcessingError";
import ExtractionItem from "@uploader/components/ExtractionItem.vue";

const { t, te, locale } = useI18n();  // eslint-disable-line @typescript-eslint/no-unused-vars

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
    if (props.extractionState != EXTRACTION_STATES.NOT_ATTEMPTED) {
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

// Dynamically choose correct intro text
const introText = computed(() => {
  if (props.extractionState === EXTRACTION_STATES.NOT_ATTEMPTED) {
    return `${t("feedback.intro-extraction-pending")}:`;
  } else if (
    props.extractionState === EXTRACTION_STATES.NO_DATA_EXTRACTED
    || props.extractionState === EXTRACTION_STATES.FAILED
  ) {
    return `${t('feedback.intro-nothing-extracted')}.`;
  } else {
    return `${t('feedback.intro-extraction-complete')}:`;
  }
});

const blueprintLookup = computed(() =>
  new Map(props.blueprints.map(bp => [bp.id, bp]))
);


function hasSucceeded(id: number): boolean {
  return blueprintUIMap[id]?.state === EXTRACTION_STATES.DATA_EXTRACTED;
}

function hasNotSucceeded(id: number): boolean {
  return blueprintUIMap[id]?.state !== EXTRACTION_STATES.DATA_EXTRACTED;
}

function hasFailed(id: number): boolean {
  return blueprintUIMap[id]?.state === EXTRACTION_STATES.FAILED;
}

/**
 * The blueprints to actually render: one entry per primary blueprint.
 * If a primary blueprint failed extraction but one of its backups
 * (in priority order) succeeded, the successful backup is shown instead.
 * Backup blueprints are otherwise never rendered on their own.
 */
const visibleBlueprints = computed(() => {
  const primaries = props.blueprints.filter(bp => !bp.is_backup);

  return primaries.map(primary => {
    if (!hasFailed(primary.id)) {
      return primary;
    }

    const successfulBackupId = (primary.backup_ids ?? [])
      .find(backupId => hasSucceeded(backupId));

    if (successfulBackupId === undefined) {
      return primary;
    }

    return blueprintLookup.value.get(successfulBackupId) ?? primary;
  });
});

const visibleBlueprintsTop = computed(() => {
    if (props.extractionState === EXTRACTION_STATES.NOT_ATTEMPTED) {
      return visibleBlueprints.value;
    } else {
      return visibleBlueprints.value.filter(bp => hasSucceeded(bp.id));
    }
  }
);

const visibleBlueprintsBottom = computed(() =>
  visibleBlueprints.value.filter(bp => hasNotSucceeded(bp.id))
);

const notSucceededExpanded = ref(false);
</script>

<template>
  <div>
    <p>{{ introText }}</p>
  </div>

  <!-- Blueprint overview -->
  <div class="extraction-items-container">
    <ExtractionItem
      v-for="blueprint in visibleBlueprintsTop"
      :key="blueprint.id"
      :blueprint="blueprint"
      :extraction-state="blueprintUIMap[blueprint.id]?.state"
      :extraction-message="blueprintUIMap[blueprint.id]?.msg"
      :extraction-error-text="blueprintUIMap[blueprint.id]?.errorText"
      :extraction-outcome="blueprintOutcomeMap[blueprint.id]"
      :has-detail-errors="blueprintUIMap[blueprint.id]?.anyDetails"
      :errors="blueprintUIMap[blueprint.id]?.errors || []"
      :combined-consent="combinedConsent"
      @consent-updated="passConsentUpdateToParent"
    />
  </div>

  <div
    v-if="visibleBlueprintsBottom.length > 0"
    class="pt-4 extraction-items-secondary-container"
  >
    <div
      v-if="extractionState != EXTRACTION_STATES.NOT_ATTEMPTED"
      class="line-to-end"
    >
      <button
        class="expansion-button"
        type="button"
        @click="notSucceededExpanded = !notSucceededExpanded"
      >
        <span
          class="expansion-icon"
          :class="{expanded: notSucceededExpanded}"
        >▸</span>
        {{ t('feedback.nothing-extracted-header') }}
      </button>
    </div>

    <div
      v-show="notSucceededExpanded"
    >
      <ExtractionItem
        v-for="blueprint in visibleBlueprintsBottom"
        :key="blueprint.id"
        :blueprint="blueprint"
        :extraction-state="blueprintUIMap[blueprint.id]?.state"
        :extraction-message="blueprintUIMap[blueprint.id]?.msg"
        :extraction-error-text="blueprintUIMap[blueprint.id]?.errorText"
        :extraction-outcome="blueprintOutcomeMap[blueprint.id]"
        :has-detail-errors="blueprintUIMap[blueprint.id]?.anyDetails"
        :errors="blueprintUIMap[blueprint.id]?.errors || []"
        :combined-consent="combinedConsent"
        @consent-updated="passConsentUpdateToParent"
      />
    </div>
  </div>
</template>

<style scoped>
.step-heading-container,
.extraction-items-container {
  order: 1;
}
.extraction-items-secondary-container {
  order: 10;
}
.expansion-button {
  font-size: var(--fs-secondary);
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  color: var(--font-color-secondary);
}

.expansion-icon {
  display: inline-block !important;
}

.expansion-icon.expanded {
  transform: rotate(90deg);
}

.line-to-end {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
}

.line-to-end::after {
  content: "";
  flex-grow: 1;
  height: 1px;
  background-color: #dbdbdb;
}
</style>

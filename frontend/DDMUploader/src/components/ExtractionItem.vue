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
 * - Computes the fieldLayout (grouping, root/nested columns) passed to
 *   ExtractionPreview/ExtractionModal for rendering extracted data
 * - Displays error messages with expandable technical details
 * - Provides consent controls for successful extractions (when not using combined consent)
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
 * - ExtractionPreview / ExtractionModal: For displaying extracted data
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
import ExtractionPreview from "@uploader/components/ExtractionPreview.vue";
import ConsentQuestion from "@uploader/components/ConsentQuestion.vue";
import {computed, ref, watch} from "vue";
import {useI18n} from "vue-i18n";
import {EntryGroup, groupEntriesByRowGroupId} from "@uploader/utils/entryGroup";
import ExtractionModal from "@uploader/components/ExtractionModal.vue";
import {ExtractionFieldLayout} from "@uploader/types/ExtractionFieldLayout";

const { t, te, locale } = useI18n();  // eslint-disable-line @typescript-eslint/no-unused-vars

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
  [EXTRACTION_STATES.DATA_EXTRACTED]: 'bi bi-file-earmark-check-fill text-success',
  [EXTRACTION_STATES.FAILED]: 'bi bi-file-earmark-x-fill text-danger',
  [EXTRACTION_STATES.NO_DATA_EXTRACTED]: 'bi bi-file-earmark-x-fill text-grey',
  [EXTRACTION_STATES.NOT_ATTEMPTED]: 'bi bi-file-earmark-fill text-grey',
  [EXTRACTION_STATES.PARTIAL]: ''
};

/**
 * Computes the icon class based on the current extraction state.
 *
 * @returns The Bootstrap icon class string for the current state
 */
const iconClass = computed(() =>
  props.extractionState ? iconStateMap[props.extractionState] : iconStateMap[EXTRACTION_STATES.NOT_ATTEMPTED]
);

const extractionPending = computed(() => props.extractionState == EXTRACTION_STATES.NOT_ATTEMPTED);
const extractionSuccess = computed(() => props.extractionState == EXTRACTION_STATES.DATA_EXTRACTED);
const nothingExtracted = computed(() => props.extractionState == EXTRACTION_STATES.NO_DATA_EXTRACTED);
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

const detailsExpanded = ref(extractionSuccess.value);
watch(extractionSuccess, (success) => {
  if (success) {
    detailsExpanded.value = true;
  }
});

const groups = computed<EntryGroup[]>(() =>
  groupEntriesByRowGroupId(props.extractionOutcome)
);

// Utils

/**
 * Whether extracted rows should be displayed as one table per root item
 * (e.g. one table per conversation) instead of a single combined table.
 * Requires both the researcher's display setting and an actually-configured
 * nested loop (nested_display_by_root_item is only ever true when a
 * nested_loop_path is set).
 */
const isGrouped = computed(() => {
  const parserConfig = props.blueprint.parser_config as { nested_loop_path?: string };
  return !!(
    props.blueprint.nested_display_by_root_item &&
    parserConfig?.nested_loop_path
  );
});

/** Field names (as used as row/extractedFieldsMap keys) that come from the nested loop. */
const nestedFieldNames = computed(() => new Set(
  props.blueprint.extraction_fields
    .filter(f => f.scope === 'nested')
    .map(f => f.alias || f.expected_name)
));

/** extractedFieldsMap keys belonging to the nested loop (the group table's own columns). */
const nestedFieldKeys = computed(() => Array.from(props.extractionOutcome.extractedFieldsMap.keys())
  .filter(key => nestedFieldNames.value.has(key)));

const rootFieldKeys = computed(() => Array.from(props.extractionOutcome.extractedFieldsMap.keys())
  .filter(key => !nestedFieldNames.value.has(key)));

const nestedColumns = computed<Map<string, string>>(() => {
  const map = new Map<string, string>();
  for (const key of nestedFieldKeys.value) {
    const label = props.extractionOutcome.extractedFieldsMap.get(key);
    if (label !== undefined) map.set(key, label);
  }
  return map;
});

const fieldLayout = computed<ExtractionFieldLayout>(() => ({
  isGrouped: isGrouped.value,
  groups: groups.value,
  rootFieldKeys: rootFieldKeys.value,
  nestedColumns: nestedColumns.value,
}));
</script>

<template>
  <div class="py-2">
    <div
      class="extraction-container"
      :class="{ 'success': extractionSuccess, 'pending': extractionPending, 'failed': extractionFailed }"
    >
      <div class="extraction-header">
        <div class="extraction-icon">
          <i :class="iconClass" />
        </div>

        <div class="extraction-header-content">
          <div class="extraction-heading">
            <template v-if="extractionPending">
              <span class="fw-bold">{{ blueprint.name }}:</span> {{ blueprint.description }}
            </template>
            <template v-else>
              <span class="fw-bold">{{ blueprint.name }}</span>
            </template>
          </div>

          <div class="extraction-header-info">
            <template v-if="extractionSuccess">
              <span v-if="!isGrouped">{{ t('feedback.x-elements-found', { nEntries: extractionOutcome.extractedData.length }) }}</span>
              <span v-else>{{ t('feedback.x-elements-found-nested', { nEntries: extractionOutcome.extractedData.length, nElements: groups.length }) }}</span>
            </template>
            <template v-if="nothingExtracted">
              <div>{{ t(`${extractionMessage}`) }}</div>
            </template>
            <template v-if="extractionFailed">
              <div>{{ extractionErrorText }}</div>
            </template>
          </div>
        </div>

        <div v-if="!extractionPending && !nothingExtracted">
          <button
            class="expansion-button"
            type="button"
            @click="detailsExpanded = !detailsExpanded"
          >
            {{ t('feedback.details') }}
            <span
              class="details-expansion-icon"
              :class="{expanded: detailsExpanded}"
            >▸</span>
          </button>
        </div>
      </div>

      <div
        v-if="!extractionPending && !nothingExtracted"
        class="extraction-info"
        :class="{ expanded: detailsExpanded }"
      >
        <!-- Success -->
        <template v-if="extractionSuccess">
          <div>
            <ExtractionPreview
              :blueprint-outcome="extractionOutcome"
              :blueprint="blueprint"
              :field-layout="fieldLayout"
            />
            <ExtractionModal
              :blueprint-outcome="extractionOutcome"
              :blueprint="blueprint"
              :field-layout="fieldLayout"
            />
          </div>
        </template>

        <!-- Failed -->
        <template v-else-if="extractionFailed">
          <div v-if="hasDetailErrors">
            <div
              role="region"
              :aria-labelledby="'error-details-summary-' + blueprint.id"
            >
              <template
                v-for="(error, i) in errors"
                :key="i"
              >
                <p
                  v-if="te(`${error.i18nDetail}-detail`)"
                  class="error-details"
                >
                  {{ t(`${error.i18nDetail}-detail`, error.context) }}
                </p>
              </template>
            </div>
          </div>
        </template>
      </div>

      <div
        v-if="extractionSuccess && combinedConsent === false"
        class="extraction-consent-container"
      >
        <div>
          <ConsentQuestion
            :combined-consent="combinedConsent"
            :blueprint="blueprint"
            :blueprint-id="blueprint.id"
            @consent-updated="passConsentUpdateToParent"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.text-grey {
  color: #d0d0d0;
}

.extraction-icon {
  padding-right: 10px;
}

.extraction-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  border: var(--border-components);
  border-radius: var(--border-radius-components);
  border-left: 4px solid var(--border-color-components);
}

.extraction-container.success {
  border-left-color: var(--ddm-success);
}

.extraction-container.error {
  border-left-color: var(--ddm-error);
}

.extraction-header {
  background: var(--bg-components);
  padding: 15px 20px;
  border-radius: var(--border-radius-components);
  display: flex;
  flex-direction: row;
}

.extraction-header-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: start;
  flex-grow: 1;
}

.extraction-header-info {
  font-size: var(--fs-secondary);
  color: var(--font-color-secondary);
}

.extraction-info {
  padding: 6px 20px 12px;
  font-size: 0.8rem !important;
  color: var(--font-color-secondary);
  display: none;
}

.extraction-info.expanded {
  display: block;
}

.extraction-consent-container {
  background: var(--bg-components);
  padding: 10px 20px;
  border-top: 1px solid var(--border-color-components);
  border-bottom-left-radius: var(--border-radius-components);
  border-bottom-right-radius: var(--border-radius-components);
}

.expansion-button {
  font-family: var(--ff-mono), monospace;
  font-size: var(--fs-secondary-mono);
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  color: var(--ddm-primary-accent);
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

.details-expansion-icon {
  display: inline-block !important;
}

.details-expansion-icon.expanded {
  transform: rotate(90deg);
}

.error-details {
  white-space: pre-line;
}

summary {
  font-weight: bold;
  padding-bottom: 5px;
}
</style>

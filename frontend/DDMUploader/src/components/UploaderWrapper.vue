<script setup lang="ts">
/**
 * Component: UploaderWrapper
 *
 * Top-level component for a single Uploader: drives the Instructions ->
 * Upload -> Review step flow and wires together file processing
 * (useFileProcessor), extraction-state tracking (useExtractionStateTracker),
 * consent (useConsentManager), and error logging (useLogPoster). Renders
 * Instructions, FileDrop, ExtractionOverview and the combined-consent
 * question depending on the active step, and emits the uploader's status
 * on every change plus 'proceed' once the user advances past the last step.
 *
 * Props:
 * - blueprintConfigs (Blueprint[]): Blueprints associated with this uploader.
 * - combinedConsent (boolean): Whether consent is asked once for all blueprints.
 * - componentId (number): Uploader id, used for DOM scoping and status/log payloads.
 * - exceptionUrl (string): Backend endpoint for error/stat logging.
 * - expectsZip (boolean): Whether the uploader accepts a ZIP or a single file.
 * - nestedZipExtractionDepth (number): How many levels of nested ZIPs to extract.
 * - instructionConfig (Instruction[]): Instruction pages (step is skipped if empty).
 * - name (string): Uploader name.
 *
 * Emits:
 * - statusChanged(uploaderId, consentMap, extractionState, blueprintStates, extractedData)
 * - proceed: Emitted when the user advances past the last step.
 */
import { useI18n } from 'vue-i18n';
import {computed, onMounted, Ref, ref, watch} from "vue";

import ConsentQuestion from "@uploader/components/ConsentQuestion.vue";
import ExtractionOverview from "@uploader/components/ExtractionOverview.vue";
import FileDrop from "@uploader/components/FileDrop.vue";
import Instructions from "@uploader/components/Instructions.vue";

import {useConsentManager} from "@uploader/composables/useConsentManager";
import {useExtractionStateTracker} from "@uploader/composables/useExtractionStateTracker";
import {useFileProcessor} from "@uploader/composables/useFileProcessor";
import {useLogPoster} from "@uploader/composables/useLogPoster";

import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";

import {Blueprint} from "@uploader/types/Blueprint";
import type {BlueprintExtractionStates, ExtractionStates} from "@uploader/types/ExtractionStates";
import {Instruction} from "@uploader/types/Instruction";
import {UPLOADER_STATES, UploaderStates} from "@uploader/types/UploaderState";

import {EXTRACTION_STATES} from "@uploader/utils/stateCatalog";
import StepIndicator from "@uploader/components/StepIndicator.vue";

const { t, locale } = useI18n();  // eslint-disable-line @typescript-eslint/no-unused-vars

const props = defineProps<{
  blueprintConfigs: Blueprint[],
  combinedConsent: boolean,
  componentId: number,
  exceptionUrl: string,
  expectsZip: boolean,
  nestedZipExtractionDepth: number,
  instructionConfig: Instruction[],
  name: string,
}>();

const emit = defineEmits<{
  (e: 'statusChanged',
   uploaderId: number,
   consentMap: Record<number, boolean>,
   extractionState: ExtractionStates,
   blueprintStates: BlueprintExtractionStates,
   extractedData: Record<number, BlueprintExtractionOutcome>
  ): void;

  (e: 'proceed'): void;
}>()

let uploaderState: Ref<UploaderStates> = ref(UPLOADER_STATES.IDLE);
const {
  generalErrors,
  blueprintOutcomeMap,
  handleSelectedFile } = useFileProcessor(props.expectsZip, props.blueprintConfigs, props.nestedZipExtractionDepth);

const { postLogs } = useLogPoster(props.componentId, props.exceptionUrl);

/**
 * Processes an uploaded file, extracts data according to blueprint configurations,
 * and updates component state.
 *
 * @param file - The user-uploaded file to process
 */
async function processFile(file: File): Promise<void> {
  uploaderState.value = UPLOADER_STATES.PROCESSING;
  await handleSelectedFile(file);
  getExtractionState();
  emitStatus();
  postLogs(generalErrors, blueprintOutcomeMap).catch(error => {
    console.error("Logs could not be posted to backend:", error);
  });
  uploaderState.value = UPLOADER_STATES.DONE;
}

const {
  extractionState,
  generalErrorsToDisplay,
  blueprintExtractionStates,
  getExtractionState } = useExtractionStateTracker(generalErrors, blueprintOutcomeMap);

const {
  blueprintConsentMap,
  updateConsent } = useConsentManager(props.blueprintConfigs, props.combinedConsent)

watch(blueprintConsentMap, () => {
    emitStatus();
  },
  { deep: true }
);

/**
 * Emits the current uploader state to the parent component.
 *
 * This includes consent status, extraction state, and all extracted data.
 */
function emitStatus(): void {
  emit(
    'statusChanged',
    props.componentId,
    blueprintConsentMap.value,
    extractionState.value,
    blueprintExtractionStates.value,
    blueprintOutcomeMap
  );
}

function emitProceed(): void {
  emit('proceed');
}

onMounted(() => {
  emitStatus();
});

const isExtractionSuccessful = computed(() =>
  extractionState.value === EXTRACTION_STATES.DATA_EXTRACTED ||
  extractionState.value === EXTRACTION_STATES.PARTIAL
);

const showCombinedConsent = computed(() =>
  props.combinedConsent === true && isExtractionSuccessful.value
);


/* Step Handling */
const INSTRUCTIONS_STEP = 'instructions';
const UPLOAD_STEP = 'upload';
const REVIEW_STEP = 'review-and-consent';

const steps = [
  INSTRUCTIONS_STEP,
  UPLOAD_STEP,
  REVIEW_STEP,
]

const activeSteps = computed(() => {
  if (props.instructionConfig.length > 0) {
    return steps;
  } else {
    return steps.filter(step => step !== INSTRUCTIONS_STEP);
  }
})

const activeStep = ref(0);

const activeStepName = computed(() => {
  return activeSteps.value[activeStep.value];
})

function nextStep(): void {
  if (activeStep.value < (activeSteps.value.length - 1)) {
    activeStep.value = activeStep.value + 1;
  } else if (activeStep.value === (activeSteps.value.length - 1)) {
    emitProceed();
  }
}

function prevStep(): void {
  if (activeStep.value > 0) {
    activeStep.value = activeStep.value - 1;
  }
}

const nextButtonHighlighted: Ref<boolean> = computed(() => {
  if (activeSteps.value[activeStep.value] === UPLOAD_STEP) {
    return !(extractionState.value === EXTRACTION_STATES.FAILED || extractionState.value === EXTRACTION_STATES.NOT_ATTEMPTED);
  } else if (activeSteps.value[activeStep.value] === REVIEW_STEP) {
    if (extractionState.value === EXTRACTION_STATES.FAILED || extractionState.value === EXTRACTION_STATES.NOT_ATTEMPTED) {
      return false;
    }

    return allConsented.value;
  }
  return true;
})

const allConsented: Ref<boolean> = computed(() => {
  for (const blueprint of Object.keys(blueprintConsentMap.value)) {
    if (blueprintConsentMap.value[blueprint] === null &&
        blueprintExtractionStates.value[blueprint].state === EXTRACTION_STATES.DATA_EXTRACTED) {
      return false;
    }
  }
  return true;
})

</script>

<template>
  <div
    :id="'ddm-uploader-' + componentId"
    class="uploader-container"
  >
    <div class="uploader-section mb-0 pb-0 pt-0">
      <StepIndicator
        :has-instructions="instructionConfig.length > 0"
        :current-step="activeStep"
      />
    </div>

    <div
      v-if="instructionConfig.length > 0"
      v-show="activeStepName === INSTRUCTIONS_STEP"
      class="uploader-section pt-3"
    >
      <Instructions
        :instructions="instructionConfig"
        :component-id="componentId"
      />
    </div>

    <div
      v-show="activeStepName === UPLOAD_STEP"
      class="uploader-section pt-3"
    >
      <FileDrop
        :expects-zip="props.expectsZip"
        :uploader-state="uploaderState"
        :extraction-state="extractionState"
        :general-errors="generalErrorsToDisplay"
        @file-dropped="processFile"
      />
    </div>

    <div
      v-show="activeStepName === REVIEW_STEP"
      class="uploader-section pt-3"
    >
      <div class="d-flex flex-column">
        <ExtractionOverview
          :uploader-state="uploaderState"
          :extraction-state="extractionState"
          :blueprints="props.blueprintConfigs"
          :blueprint-extraction-states="blueprintExtractionStates"
          :blueprint-outcome-map="blueprintOutcomeMap"
          :combined-consent="combinedConsent"
          @consent-updated="updateConsent"
        />

        <div
          v-if="showCombinedConsent"
          class="combined-consent-container mt-4 mb-2"
        >
          <ConsentQuestion
            :combined-consent="combinedConsent"
            :blueprint="null"
            :blueprint-id="null"
            @consent-updated="updateConsent"
          />
        </div>
      </div>
    </div>
  </div>

  <div class="d-flex flex-row justify-content-between">
    <button
      type="button"
      class="ddm-primary-button-base"
      :class="{ 'is-invisible': activeStep === 0 }"
      @click="prevStep"
    >
      <i class="step-chevron bi bi-chevron-left" />
      <span class="ps-2">{{ t('step-indicator.button-prev') }}</span>
    </button>
    <button
      v-show="activeStep <= (activeSteps.length - 1)"
      type="button"
      class="ddm-primary-button-base"
      :class="{'ddm-primary-button': nextButtonHighlighted}"
      @click="nextStep"
    >
      <span class="pe-2">{{ t('step-indicator.button-next') }}</span>
      <i class="step-chevron bi bi-chevron-right" />
    </button>
  </div>
</template>

<style scoped>
.is-invisible {
  visibility: hidden;
}

.uploader-container {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.combined-consent-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  border: var(--border-components);
  border-radius: var(--border-radius-components);
  background-color: var(--bg-components);
  order: 2;
  padding: 15px 20px;
  font-weight: bold !important;
}

.uploader-section {
  padding: 30px 20px;
}

@media (min-width: 768px) {
  .uploader-container {
    border: none;
  }

  .uploader-container .uploader-section:last-child {
    padding: 40px 20px 30px 20px;
  }

  .uploader-container .uploader-section:first-child {
    padding: 30px 20px 40px 20px;
  }

}
</style>

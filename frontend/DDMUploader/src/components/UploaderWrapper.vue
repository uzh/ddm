<script setup lang="ts">
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

const { t, locale } = useI18n();

const props = defineProps<{
  blueprintConfigs: Blueprint[],
  combinedConsent: boolean,
  componentId: number,
  exceptionUrl: string,
  expectsZip: boolean,
  instructionConfig: Instruction[],
  name: string,
}>();

const emit = defineEmits<{
  (e: 'statusChanged',
   uploaderId: number,
   consentMap: Record<number, boolean>,
   extractionState: ExtractionStates,
   blueprintStates: BlueprintExtractionStates,
   extractedData: BlueprintExtractionOutcome[]
  ): void;
}>()

let uploaderState: Ref<UploaderStates> = ref(UPLOADER_STATES.IDLE);
const {
  generalErrors,
  blueprintOutcomeMap,
  handleSelectedFile } = useFileProcessor(props.expectsZip, props.blueprintConfigs);

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

onMounted(() => {
  emitStatus();
});

const isExtractionSuccessful = computed(() =>
  extractionState.value === EXTRACTION_STATES.SUCCESS ||
  extractionState.value === EXTRACTION_STATES.PARTIAL
);

const showCombinedConsent = computed(() =>
  props.combinedConsent === true && isExtractionSuccessful.value
);

</script>

<template>

  <div class="uploader-name">{{ name }}</div>
  <div class="uploader-container">
    <div v-if="instructionConfig.length > 0"
         class="uploader-section">
      <Instructions
        :instructions="instructionConfig"
        :component-id="componentId"
      />
    </div>

    <div class="uploader-section">
      <FileDrop
          :expects-zip="props.expectsZip"
          :uploader-state="uploaderState"
          :extraction-state="extractionState"
          :general-errors="generalErrorsToDisplay"
          @fileDropped="processFile"
      />
    </div>

    <div class="uploader-section">
      <ExtractionOverview
          :uploader-state="uploaderState"
          :extraction-state="extractionState"
          :blueprints="props.blueprintConfigs"
          :blueprint-extraction-states="blueprintExtractionStates"
          :blueprint-outcome-map="blueprintOutcomeMap"
          :combined-consent="combinedConsent"
          @consentUpdated="updateConsent"
      />
    </div>

    <div v-if="showCombinedConsent"
         class="uploader-section">
      <ConsentQuestion
          :combined-consent="combinedConsent"
          :blueprint-id="null"
          @consentUpdated="updateConsent"
      />
    </div>
  </div>
</template>

<style scoped>
.uploader-container {
  border-top: 2px solid #000;
  border-bottom: 2px solid #000;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.uploader-container .uploader-section:not(:last-child) {
  border-bottom: 3px solid #dee2e6;
}

.uploader-container .uploader-section:not(:first-child),
.uploader-container .uploader-section:not(:last-child) {
  padding: 40px 0 40px 0;
}

.uploader-container .uploader-section:first-child {
  padding: 10px 0 40px 0;
}

.uploader-container .uploader-section:last-child {
  padding: 40px 0 30px 0;
}


.uploader-name {
  font-weight: bold;
  font-size: 1.5rem;
  padding-bottom: 0.5rem;
}

.uploader-section {
  padding: 30px 20px;
}

@media (min-width: 768px) {
  .uploader-container {
    box-shadow: 6px 7px 20px #80808040;
    border-radius: 8px;
    border: none;
  }

  .uploader-container .uploader-section:not(:first-child),
  .uploader-container .uploader-section:not(:last-child) {
    padding: 40px 20px;
  }

  .uploader-container .uploader-section:last-child {
    padding: 40px 20px 30px 20px;
  }

  .uploader-container .uploader-section:first-child {
    padding: 30px 20px 40px 20px;
  }

}
</style>
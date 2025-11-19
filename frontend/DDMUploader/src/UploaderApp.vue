<script setup lang="ts">
/**
 * Main entry component for handling 1-n uploaders.
 *
 * Features:
 * - Dynamically renders uploader components from config.
 * - Validates uploader state before submission regarding two aspects:
 *      a. Has the user attempted an upload for all uploaders?
 *      b. Has the user explicitly (not) consented to the submission of all extracted blueprint data?
 *   If the answer to a. or b. is 'no', the user will see a modal when trying to submit the data donation.
 *   In case a. the user can choose to submit (i.e., skip) the donation anyway (there is a continue button on the modal).
 *   In case b. the user cannot continue until they have explicitly answered all consent questions (the continue button is hidden).
 * - Submits extracted data via a centralized data submission composable.
 *
 * Props:
 * - uploaderConfigs: Array of uploader configurations (name, blueprints, etc.)
 * - actionUrl: Endpoint for final submission of data.
 * - exceptionUrl: Logging endpoint for errors or diagnostics.
 * - language: Current UI language code (e.g., 'en', 'de').
 * - csrfToken: Token for securing form submission.
 */

import {useI18n} from 'vue-i18n';
import {Ref, ref} from 'vue';
import UploaderWrapper from "@uploader/components/UploaderWrapper.vue";
import type {BlueprintExtractionStates, ExtractionStates} from "@uploader/types/ExtractionStates";
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";
import IssueModal from "@uploader/components/IssueModal.vue";
import {useUploaderValidator} from "@uploader/composables/useUploaderValidator";
import {useDataSubmitter} from "@uploader/composables/useDataSubmitter";
import {UploaderOutcome} from "@uploader/types/UploaderOutcome";
import SubmittingOverlay from "@uploader/components/SubmittingOverlay.vue";
import {UploaderConfig} from "@uploader/types/UploaderConfig";

const { t, locale } = useI18n();

const props = defineProps<{
  uploaderConfigs: UploaderConfig[];
  actionUrl: string,
  exceptionUrl: string,
  language: string,
  csrfToken: string
}>();

const uploaderOutcomes: Ref<Record<number, UploaderOutcome>> = ref(initializeUploaderOutcomes());  // Used to track and validate the uploader states.

const {
  validateUploaders,
  failedUploaderNames,
  unattendedUploaderShare,
  unattendedUploaderNames,
  blueprintsWithoutConsentCount,
  blueprintsWithoutConsentNames,
  allUploadersValid } = useUploaderValidator(uploaderOutcomes);

const {
  submitting,
  submitDonation } = useDataSubmitter(uploaderOutcomes, props.actionUrl);

/**
 * Updates the outcome state of a specific uploader based on user interactions and extraction results.
 *
 * This function serves as a central callback for uploader components, consolidating all
 * uploader state changes in one place for validation and submission purposes.
 *
 * @param componentId - Unique identifier for the uploader component
 * @param consentMap - User consent decisions mapped by blueprint ID
 * @param extractionState - Overall extraction status (success, partial, error) of the uploader
 * @param blueprintStates - Detailed extraction state for each blueprint mapped by blueprint ID
 * @param extractionOutcomes - Extracted data and metadata for each blueprint mapped by blueprint ID
 */
function updateUploaderOutcome(
    componentId: number,
    consentMap: Record<number, boolean>,
    extractionState: ExtractionStates,
    blueprintStates: BlueprintExtractionStates,
    extractionOutcomes: Record<number, BlueprintExtractionOutcome>
): void {
  const outcome = uploaderOutcomes.value[componentId];
  if (outcome) {
    Object.assign(outcome, {
      consentMap: consentMap,
      uploaderState: extractionState,
      blueprintStates: blueprintStates,
      extractionOutcome: extractionOutcomes,
    });
  }
}

let showModal: Ref<boolean> = ref(false);

function hideModal(): void {
  showModal.value = false;
}

/**
 * Handles the "Next" button click, triggering validation and conditionally showing issues or submitting data.
 *
 * This function orchestrates the final steps in the upload workflow:
 * 1. Validates all uploader states
 * 2. If validation issues exist, displays the issue modal
 * 3. If validation passes, submits the data donation
 */
function proceed(): void {
  validateUploaders();
  if (!allUploadersValid.value) {
    showModal.value = true;
  } else {
    submitDonation();
  }
}

/**
 * Creates a lookup map that connects blueprint IDs to their human-readable names.
 *
 * @param uploader - The configuration object for an uploader component
 * @returns A record with blueprint IDs as keys and names as values
 */
function getBlueprintNameMap(uploader: UploaderConfig): Record<number, string> {
  const names: Record<number, string> = {};
  for (const blueprint of uploader.blueprints) {
    names[blueprint.id] = blueprint.name;
  }
  return names;
}

function initializeUploaderOutcomes(): Record<number, UploaderOutcome> {
  const initializedRecord: Record<number, UploaderOutcome> = {};
  for (const uploader of props.uploaderConfigs) {
    initializedRecord[uploader.uploader_id] = {
      uploaderName: uploader.name,
      blueprintNames: getBlueprintNameMap(uploader),
      consentMap: null,
      uploaderState: null,
      blueprintStates: null,
      extractionOutcome: null,
    };
  }
  return initializedRecord;
}
</script>

<template>
  <template v-for="config in uploaderConfigs">
    <div class="ddm-uploader">
      <UploaderWrapper
          :blueprint-configs="config.blueprints"
          :combined-consent="config.combined_consent"
          :componentId="config.uploader_id"
          :exception-url="props.exceptionUrl"
          :expects-zip="config.upload_type === 'zip file'"
          :instruction-config="config.instructions"
          :name="config.name"
          @statusChanged="updateUploaderOutcome"
      />
    </div>
  </template>

  <IssueModal
      :failed-uploader-names="failedUploaderNames"
      :unattended-uploader-share="unattendedUploaderShare"
      :unattended-uploader-names="unattendedUploaderNames"
      :blueprints-without-consent-count="blueprintsWithoutConsentCount"
      :blueprints-without-consent-names="blueprintsWithoutConsentNames"
      :all-uploaders-valid="allUploadersValid"
      :show-modal="showModal"
      @continueAnyway="submitDonation"
      @modal-closed="hideModal"
  />

  <SubmittingOverlay v-if="submitting" />

  <div class="row">
    <div class="col">
      <button
          class="flow-btn"
          type="button"
          @click="proceed"
      >{{ t('uploader-app.next-btn') }}&nbsp;&nbsp;&#8250;</button>
    </div>
  </div>

  <form id="uploader-form" method="POST" enctype="multipart/form-data" v-show="false">
    <input type="hidden" name="csrfmiddlewaretoken" :value="csrfToken">
  </form>

</template>

<style>
.modal-open {
  overflow: hidden;
}

.section-heading {
  font-size: 1.35rem;
}

.section-icon {
  font-size: 2rem;
  width: 50px;
}

.color-red {
  color: #d90015 !important;
}
</style>

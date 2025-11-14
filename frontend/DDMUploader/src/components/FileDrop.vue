<script setup lang="ts">
/**
 * Component: FileDrop
 *
 * This component handles file uploads through both drag-and-drop and file picker inputs.
 * It provides visual feedback for different processing states (idle, processing, done),
 * supports retrying a file upload, and displays errors if extraction fails.
 *
 * Features:
 * - Drag-and-drop file upload area with hover effects.
 * - File picker when clicking the drop zone.
 * - Shows different UI states based on the processor and extraction status:
 *   - Idle: Prompt user to drop/select a file.
 *   - Processing: Display a loading spinner.
 *   - Done: Show success, failure, or no-data messages.
 * - Allows retrying file uploads after failure or success.
 * - Displays localized error messages for general extraction errors.
 * - Adapts accepted file types dynamically (e.g., ZIP files if needed).
 *
 * Props:
 * - expectsZip (boolean): Whether the component should only accept .zip files as uploads.
 * - uploaderState (UploaderState): Current state of the uploader ('idle', 'processing', 'done').
 * - extractionState (ExtractionStates): Outcome of the extraction process.
 * - generalErrors (ProcessingError[]): List of general errors encountered during extraction.
 *
 * Emits:
 * - fileDropped(file: File): Triggered when the user selects or drops a new file.
 *
 * Internal Utilities:
 * - initialize(): Sets up accepted file input types based on props.
 * - handleDrop(event: DragEvent): Handles files dropped into the area.
 * - handleFileInput(event: Event): Handles file selection via input element.
 *
 * Dependencies:
 * - vue-i18n: For translation and localization of all user-facing text.
 */


import {onMounted, toRef, ref, watch, computed} from 'vue';
import { useI18n } from 'vue-i18n';
import {ExtractionStates} from "@uploader/types/extractionStates";
import {EXTRACTION_STATES} from "@uploader/utils/stateCatalog";
import {UPLOADER_STATES, UploaderStates} from "@uploader/types/UploaderState";
import {ProcessingError} from "@uploader/types/ProcessingError";

const { t, locale } = useI18n();

const props = defineProps<{
  expectsZip: boolean,
  uploaderState: UploaderStates,
  extractionState: ExtractionStates,
  generalErrors: ProcessingError[]
}>();

const emit = defineEmits<{
  (e: 'fileDropped', file: File): void;
}>();

const isDragging = ref<boolean>(false);
const retryRequested = ref<boolean>(false);
const acceptedFileInput = ref<string>('');
const extractionState = toRef(props, 'extractionState');
const fileSelectorBorderClass = ref<string>('bg-lightgrey');

onMounted(() => {
  initialize();
});

const borderClassMap: Record<ExtractionStates, string> = {
  [EXTRACTION_STATES.SUCCESS]: 'border-success',
  [EXTRACTION_STATES.PARTIAL]: 'border-success',
  [EXTRACTION_STATES.FAILED]: 'border-failed',
  [EXTRACTION_STATES.NO_DATA]: 'border-no-data',
  [EXTRACTION_STATES.PENDING]: 'bg-lightgrey'
};

watch(extractionState, (val: ExtractionStates) => {
  fileSelectorBorderClass.value = borderClassMap[val];
});

/**
 * Initializes the component's file input settings based on props.
 *
 * Sets the accepted file types for the file input element based on
 * whether the component expects ZIP files or other formats.
 */
function initialize() {
  if (props.expectsZip) {
    acceptedFileInput.value = '.zip,application/zip,application/x-zip-compressed,multipart/x-zip'
  } else {
    acceptedFileInput.value = 'application/json,text/csv,.csv,.json'
  }
}

/**
 * Handles file drop events when users drag and drop files onto the component.
 *
 * Prevents default browser behavior, extracts the file from the drop event,
 * and emits the fileDropped event with the selected file.
 *
 * @param event - The drag event containing dropped files
 */
function handleDrop(event: DragEvent) {
  event.preventDefault();
  isDragging.value = false;

  const files = event.dataTransfer?.files;
  if (files?.[0]) {
    retryRequested.value = false;
    emit('fileDropped', files[0]);
  }
}

function handleFileInput(event: Event) {
  const input = event.target as HTMLInputElement;
  const files = input.files;

  if (!files || files.length === 0) return;

  const file = files[0];
  retryRequested.value = false;
  emit('fileDropped', file);
}

/**
 * Resets the uploader to allow selecting a new file.
 *
 * This function:
 * 1. Sets the retryRequested flag to show the file selection UI
 * 2. Resets the background styling to the default state
 */
function resetUploader(): void {
  retryRequested.value = true;
  fileSelectorBorderClass.value = 'bg-lightgrey';
}

const showFileSelector = computed(() =>
  props.uploaderState === UPLOADER_STATES.IDLE || retryRequested.value
);

const showProcessingIndicator = computed(() =>
  props.uploaderState === UPLOADER_STATES.PROCESSING
);

const showResults = computed(() =>
  props.uploaderState === UPLOADER_STATES.DONE
);

const showRetryButton = computed(() =>
  props.uploaderState === UPLOADER_STATES.DONE &&
  props.extractionState !== EXTRACTION_STATES.FAILED &&
  !retryRequested.value
);

const extractionSuccess = computed(() =>
  props.extractionState === EXTRACTION_STATES.SUCCESS ||
  props.extractionState === EXTRACTION_STATES.PARTIAL
);

const extractionFailed = computed(() =>
  props.extractionState === EXTRACTION_STATES.FAILED
);

const extractionNoData = computed(() =>
  props.extractionState === EXTRACTION_STATES.NO_DATA
);
</script>

<template>
  <div class="d-lg-flex flex-row align-items-center justify-content-between">

    <div class="pe-5 pb-3 pb-lg-0 d-flex align-items-center ">
      <span class="section-icon">
        <i v-if="['success', 'partial'].includes(props.extractionState)" class="bi bi-check-square fs-2 pe-3 text-success"></i>
        <i v-else class="bi bi-upload fs-2 pe-3"></i>
      </span>
      <span class="section-heading">{{ t("file-drop.heading") }}</span>
    </div>

    <div class="flex-grow-1">

      <div class="border rounded text-center position-relative bg-lightgrey" :class="fileSelectorBorderClass">
        <!-- Processing pending -->
        <div v-if="showFileSelector"
             class="p-4"
             :class="{ 'dropzone-hover': isDragging }"
             @dragover.prevent="isDragging = true"
             @dragleave.prevent="isDragging = false"
             @drop="handleDrop"
             @click="$refs.fileInput.click()"
             style="cursor: pointer;"
        >
          <p class="mb-0">
            <i id="ul-modal-info-icon" class="bi bi-upload fs-5 pe-3"></i>
            <span v-if="!isDragging" class="ps-2 fw-bold fs-6">{{ t('file-drop.selection-prompt') }}</span>
            <span v-if="isDragging" class="ps-2 fw-bold fs-6">{{ t('file-drop.release-to-select') }}</span>
          </p>
          <input
            ref="fileInput"
            type="file"
            class="d-none"
            :accept="acceptedFileInput"
            @change="handleFileInput"
          />
        </div>

        <!-- Processing ongoing -->
        <div v-else-if="showProcessingIndicator"
             class="d-flex align-items-center justify-content-center p-4">
          <span class="spinner-border float-right me-3" role="status"><span class="sr-only"></span></span>
          <p class="mb-0">{{ t('file-drop.file-is-being-processed') }}</p>
        </div>

        <!-- Processing complete -->
        <div v-else-if="showResults" class="p-4">

          <div v-if="extractionSuccess">
            <p class="fs-5 fw-bold text-success"><i class="bi bi-check-circle pe-3"></i>{{ t('file-drop.processing-success') }}</p>
            {{ t('extraction-state.file.success') }}
          </div>

          <div v-else-if="extractionFailed">
            <p class="fs-5 fw-bold color-red">{{ t('file-drop.processing-failed') }}</p>

            <div v-if="props.generalErrors.length">
              <p v-for="(error, i) in props.generalErrors" :key="i" class="pt-3 color-darkred">
                {{ t(error.i18nDetail, error.context) }}
              </p>
            </div>

            <p class="pt-2">{{ t('file-drop.retry-hint') }} <a class="btn re-try-btn fs-6" @click="resetUploader">{{ t('file-drop.choose-different-file') }}</a></p>
          </div>

          <div v-else-if="extractionNoData">
            <p class="fs-5 fw-bold">{{ t('file-drop.processing-complete') }}</p>
            {{ t('extraction-state.file.no-data-extracted') }}
          </div>
        </div>
      </div>

      <!-- Retry button -->
      <div v-if="showRetryButton" class="pt-2 w-100 text-center">
        <a class="btn re-try-btn fs-6" @click="resetUploader">{{ t('file-drop.choose-different-file') }}</a>
      </div>

    </div>

  </div>
</template>

<style scoped>
* {
  --color-success: #198754;
  --color-failed: #d90015;
  --color-no-data: #0272ff;
  --color-light-bg: #f8f9fa;
  --color-hover-bg: #efefef;
  --color-dark-grey: #6c6c6c;
}

.bg-lightgrey {
  background-color:  var(--color-light-bg);
}
.dropzone-hover {
  background-color: var(--color-hover-bg) !important;
}
.re-try-btn {
  background-color: #ededed;
  color: var(--color-dark-grey);
  font-size: 0.9rem !important;
  padding: 2px 8px 2px 8px !important;
}
.re-try-btn:hover {
  background-color: #dddddd;
  cursor: pointer;
  color: var(--color-dark-grey) !important;
}
.border-success {
  border-color: var(--color-success) !important;
}
.border-failed {
  border-color: var(--color-failed) !important;
}
.border-no-data {
  border-color: var(--color-no-data) !important;
}
.color-darkred {
  color: darkred !important;
}
</style>

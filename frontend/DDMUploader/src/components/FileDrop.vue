<script setup lang="ts">
/**
 * Component: FileDrop
 *
 * Handles file uploads via drag-and-drop or a file picker, showing
 * different UI per state (idle prompt, processing spinner, success/failure/
 * no-data result), and lets the user retry with a different file. Accepted
 * file types adapt based on whether a ZIP is expected.
 *
 * Props:
 * - expectsZip (boolean): Whether the component should only accept .zip files as uploads.
 * - uploaderState (UploaderState): Current state of the uploader ('idle', 'processing', 'done').
 * - extractionState (ExtractionStates): Outcome of the extraction process.
 * - generalErrors (ProcessingError[]): List of general errors encountered during extraction.
 *
 * Emits:
 * - fileDropped(file: File): Triggered when the user selects or drops a new file.
 */


import {computed, nextTick, onMounted, ref, toRef, useTemplateRef, watch} from 'vue';
import { useTranslation } from '@uploader/composables/useTranslation';
import {ExtractionStates} from '@uploader/types/ExtractionStates';
import {EXTRACTION_STATES} from '@uploader/utils/stateCatalog';
import {UPLOADER_STATES, UploaderStates} from '@uploader/types/UploaderState';
import {ProcessingError} from '@uploader/types/ProcessingError';

const { t, locale } = useTranslation();  // eslint-disable-line @typescript-eslint/no-unused-vars

const props = defineProps<{
  expectsZip: boolean,
  uploaderState: UploaderStates,
  extractionState: ExtractionStates,
  generalErrors: ProcessingError[]
}>();

const emit = defineEmits<{
  (e: 'fileDropped', file: File): void;
}>();

const fileInput = useTemplateRef('fileInput');

const isDragging = ref<boolean>(false);
const retryRequested = ref<boolean>(false);
const acceptedFileInput = ref<string>('');
const extractionState = toRef(props, 'extractionState');
const fileSelectorBorderClass = ref<string>('bg-lightgrey');

onMounted(() => {
  initialize();
});

const borderClassMap: Record<ExtractionStates, string> = {
  [EXTRACTION_STATES.DATA_EXTRACTED]: 'border-success',
  [EXTRACTION_STATES.PARTIAL]: 'border-success',
  [EXTRACTION_STATES.FAILED]: 'border-failed',
  [EXTRACTION_STATES.NO_DATA_EXTRACTED]: 'border-no-data',
  [EXTRACTION_STATES.NOT_ATTEMPTED]: 'bg-lightgrey'
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
 * Resets the uploader and opens dialog to select a new file.
 *
 * This function:
 * 1. Sets the retryRequested flag to show the file selection UI
 * 2. Resets the background styling to the default state
 * 3. Opens the file chooser
 */
function chooseDifferentFile(): void {
  retryRequested.value = true;
  fileSelectorBorderClass.value = 'bg-lightgrey';

  nextTick(() => {
    fileInput.value?.click();
  });
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
  props.extractionState === EXTRACTION_STATES.DATA_EXTRACTED ||
  props.extractionState === EXTRACTION_STATES.PARTIAL
);

const extractionFailed = computed(() =>
  props.extractionState === EXTRACTION_STATES.FAILED
);

const extractionNoData = computed(() =>
  props.extractionState === EXTRACTION_STATES.NO_DATA_EXTRACTED
);
</script>

<template>
  <div class="ddm-file-drop d-lg-flex flex-row align-items-center justify-content-between">
    <div class="flex-grow-1">
      <div
        class="text-center position-relative"
        :class="fileSelectorBorderClass"
      >
        <!-- Processing pending -->
        <div
          v-if="showFileSelector"
          class="p-4 ddm-dropzone ddm-dropzone-clickable"
          :class="{ 'dropzone-hover': isDragging }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop="handleDrop"
          @click="$refs.fileInput.click()"
        >
          <div class="dropzone-icon">
            <i class="bi bi-upload" />
          </div>

          <div class="dropzone-label">
            <span
              v-if="!isDragging"
              class="fw-bold fs-6"
            >
              {{ t('file-drop.selection-prompt') }}
            </span>
            <span
              v-if="isDragging"
              class="fw-bold fs-6"
            >
              {{ t('file-drop.release-to-select') }}
            </span>
          </div>

          <div class="dropzone-info">
            {{ t('file-drop.relevant-data-hint') }}
          </div>

          <input
            ref="fileInput"
            type="file"
            class="d-none"
            :accept="acceptedFileInput"
            @change="handleFileInput"
          >
        </div>

        <!-- Processing ongoing -->
        <div
          v-else-if="showProcessingIndicator"
          class="ddm-dropzone"
        >
          <div class="dropzone-icon">
            <span
              class="spinner-border float-right"
              role="status"
            >
              <span class="sr-only" />
            </span>
          </div>

          <div class="dropzone-info">
            {{ t('file-drop.file-is-being-processed') }}
          </div>
        </div>

        <!-- Processing complete -->
        <div
          v-else-if="showResults"
          class="ddm-dropzone"
        >
          <template v-if="extractionSuccess">
            <div class="dropzone-icon fc-success">
              <i class="bi bi-check-circle" />
            </div>

            <div class="dropzone-label">
              {{ t('file-drop.processing-success') }}
            </div>

            <div class="dropzone-info">
              {{ t('extraction-state.file.success') }}
            </div>
          </template>

          <template v-else-if="extractionFailed">
            <div class="dropzone-label">
              {{ t('file-drop.something-went-wrong') }}
            </div>

            <div
              v-if="props.generalErrors.length"
              class="dropzone-info error-info-container"
            >
              <p
                v-for="(error, i) in props.generalErrors"
                :key="i"
                class="pt-3 fc-error"
              >
                {{ t(error.i18nDetail, error.context) }}
              </p>
            </div>

            <div class="dropzone-info">
              {{ t('file-drop.retry-hint') }}
            </div>

            <div class="dropzone-retry">
              <button
                class="ddm-secondary-button ddm-primary-button mt-2"
                @click="chooseDifferentFile"
              >
                {{ t('file-drop.choose-different-file') }}
              </button>
            </div>
          </template>

          <template v-else-if="extractionNoData">
            <div class="dropzone-icon">
              <i class="bi bi-upload fs-4 pb-4" />
            </div>

            <div class="dropzone-label">
              {{ t('file-drop.processing-complete') }}
            </div>

            <div class="dropzone-info">
              {{ t('extraction-state.file.no-data-extracted') }}
            </div>
          </template>
        </div>
      </div>

      <!-- Retry button -->
      <div
        v-if="showRetryButton"
        class="pt-2 w-100 text-center retry-button-container"
      >
        <button
          class="ddm-secondary-button"
          @click="chooseDifferentFile"
        >
          {{ t('file-drop.choose-different-file') }}
        </button>
      </div>
    </div>
  </div>

  <div class="upload-info">
    <div class="upload-info-icon">
      <i class="bi bi-lock-fill" />
    </div>
    <div class="upload-info-text">
      {{ t('file-drop.upload-info') }}
    </div>
  </div>
</template>

<style scoped>
@import "@uploader/assets/styles/buttons.css";

.ddm-dropzone {
  border: var(--border-components);
  border-radius: var(--border-radius-components);
  background: var(--bg-components);
  min-height: 300px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.ddm-dropzone-clickable {
  cursor: pointer;
}

.ddm-dropzone-clickable:hover {
  background: color-mix(in oklab, var(--ddm-primary-accent), white 90%);
}

.dropzone-icon {
  padding-bottom: 10px;
  font-size: 1.5rem;
}

.dropzone-label {
  font-weight: bold;

}

.dropzone-info {
  color: var(--font-color-secondary);
  font-size: var(--fs-secondary);
  padding-top: 4px;
}

.error-info-container {
  border: 1px solid var(--ddm-error);
  border-radius: var(--border-radius);
  background: color-mix(in oklab, var(--ddm-error), white 95%);
  margin-top: 15px;
  margin-bottom: 15px;
  padding-left: 15px;
  padding-right: 15px;
}

.upload-info {
  margin-top: 20px;
  padding: 20px;
  border: 1px solid grey;
  border-radius: 3px;
  background: #e1ffe9;
  color: var(--font-color-secondary);
  font-size: var(--fs-secondary);
  display: flex;
  flex-direction: row;
  justify-content: center;
}

.upload-info-icon {
  padding-right: 10px;
}

.bg-lightgrey {
  background-color: var(--ddm-file-bg);
}
.dropzone-hover {
  background-color: var(--ddm-file-bg-hover) !important;
}
.border-success {
  border-color: var(--ddm-success) !important;
}
.border-failed {
  border-color: var(--ddm-error) !important;
}
.border-no-data {
  border-color: var(--ddm-no-data) !important;
}
.color-darkred {
  color: darkred !important;
}
</style>

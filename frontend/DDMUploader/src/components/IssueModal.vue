<script setup lang="ts">
/**
 * Component: IssueModal
 *
 * A modal dialog shown before submission when validation finds issues
 * (uploaders not attempted, failed uploaders, or blueprints missing
 * consent). If any blueprint lacks consent, "Continue Anyway" is hidden
 * and the user must go back; otherwise they can dismiss and proceed.
 *
 * Props:
 * - failedUploaderNames: Names of the uploaders that have status "failed"
 * - unattendedUploaderShare: Percentage (0-1) of uploaders the user hasn't attempted
 * - unattendedUploaderNames: Names of the uploaders that haven't been attempted
 * - blueprintsWithoutConsentCount: Number of blueprints without explicit consent
 * - blueprintsWithoutConsentNames: Names of the blueprints without consent
 * - allUploadersValid: Whether all uploaders pass validation requirements
 * - showModal: Toggle to control modal visibility
 *
 * Emits:
 * - continueAnyway: Emitted when user chooses to continue despite warnings
 * - modalClosed: Emitted when modal is closed via the back button
 */

import { useTranslation } from '@uploader/composables/useTranslation';
import {computed, onMounted, onUnmounted, ref, Ref, watch} from "vue";
const { t, locale } = useTranslation();  // eslint-disable-line @typescript-eslint/no-unused-vars

const props = defineProps<{
  failedUploaderNames: string[],
  unattendedUploaderShare: number,
  unattendedUploaderNames: string[],
  blueprintsWithoutConsentCount: number,
  blueprintsWithoutConsentNames: string[],
  allUploadersValid: boolean | null,
  showModal: boolean
}>();

const emit = defineEmits<{
  (e: 'continueAnyway'): void;
  (e: 'modalClosed'): void;
}>();

const modalVisible: Ref<boolean> = ref(false);
const canContinueAnyway = computed(() => props.blueprintsWithoutConsentCount === 0);

watch(() => props.showModal, () => {
  modalVisible.value = props.showModal;
  if (modalVisible.value === true) {
    document.body.classList.add('modal-open');
  }
}, { immediate: true });

/**
 * Hides the modal and emits the modalClosed event.
 * This allows the parent component to update its state accordingly.
 */
const hideModal = (): void => {
  modalVisible.value = false;
  emit('modalClosed');
  document.body.classList.remove('modal-open');
}

/**
 * Formats an array of strings into a human-readable list.
 *
 * Example: ['A', 'B', 'C'] becomes ' ("A", "B", "C")'
 *
 * @param strings - Array of strings to combine
 * @returns A formatted string with all items enclosed in quotes and properly separated
 */
const combineStrings = (strings: string[]): string => {
  const nStrings: number = strings.length;
  if (nStrings === 0) {
    return '';
  }

  let combinedString: string = '';
  for (let i = 0; i < nStrings; i++) {
    combinedString += ('"' + strings[i] + '"');
    if (i < nStrings - 2) {
      combinedString += ', ';
    } else if (i === nStrings - 2) {
      combinedString += ', ';
    }
  }
  return combinedString;
}

function handleKeyDown(event: KeyboardEvent): void {
  if (event.key === 'Escape') {
    hideModal();
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
});
</script>

<template>
  <template v-if="modalVisible">
    <div
      class="modal-backdrop"
      @click="hideModal"
    />

    <div class="modal-container">
      <div
        class="issue-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        tabindex="-1"
      >
        <div class="modal-body">
          <h3
            id="modal-title"
            class="mb-3"
          >
            {{ t("issue-modal.title") }}
          </h3>
          <div class="modal-text">
            <p
              v-if="unattendedUploaderShare === 1"
              class="m-0"
            >
              {{ t("issue-modal.none-attempted") }}
            </p>
            <p
              v-else-if="blueprintsWithoutConsentCount > 0 && unattendedUploaderShare < 1"
              class="m-0"
            >
              {{ t("issue-modal.not-all-consented", {"blueprints-wo-consent": combineStrings(props.blueprintsWithoutConsentNames)}) }}
            </p>
            <p
              v-else-if="unattendedUploaderShare > 0"
              class="m-0"
            >
              {{ t("issue-modal.not-all-attempted", {"skipped-uploads": combineStrings(props.unattendedUploaderNames)}) }}
            </p>
            <p
              v-else-if="failedUploaderNames.length > 0"
              class="m-0"
            >
              {{ t("issue-modal.failed-uploaders", {"uploads": combineStrings(props.failedUploaderNames)}) }}
            </p>
          </div>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="ddm-primary-button-base ddm-primary-button"
            @click="hideModal"
          >
            {{ t("issue-modal.back") }}
          </button>

          <button
            v-if="canContinueAnyway"
            type="button"
            class="ddm-primary-button-base"
            @click="hideModal(); emit('continueAnyway')"
          >
            {{ t("issue-modal.continue-anyway") }}
          </button>
        </div>
      </div>
    </div>
  </template>
</template>

<style scoped>
@import "@uploader/assets/styles/buttons.css";

.modal-container {
  position: fixed;
  height: 100vh;
  width: 100%;
  top: 0;
  left: 0;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.issue-modal {
  display: flex;
  flex-direction: column;
  background: white;
  z-index: 2000;
  max-height: 90%;
  border-radius: var(--border-radius-components);
}

.modal-backdrop {
  position: fixed;
  height: 100%;
  width: 100%;
  background: #959595;
  opacity: .75;
  z-index: 1000;
}

.modal-body {
  display: flex;
  flex-direction: column !important;
  overflow: hidden;
  flex: 1;
  min-height: 0;
  padding: 1rem;
}

.modal-text {
  min-height: 0;
  min-width: 0;
  flex: 1;
  overflow-y: auto;
  text-align: center;
  align-self: stretch;
  white-space: pre-line;
}

.modal-footer {
  justify-content: center;
}

@media (min-width: 768px) {
  .issue-modal {
    width: 70%;
    max-width: 1000px;
  }

  .modal-body {
    flex-direction: row;
    align-items: flex-start;
    padding: 1.5rem 2rem;
  }

  .modal-text {
    text-align: left;
  }

  .modal-footer {
    justify-content: flex-end;
  }
}
</style>

<script setup lang="ts">
/**
 * Component: IssueModal
 *
 * A modal dialog that displays validation issues before form submission.
 * It alerts users about incomplete actions and provides options to proceed
 * or go back depending on the severity of issues.
 *
 * Features:
 * - Shows different messages based on validation state:
 *   - Unattended uploaders: Displays names of uploaders the user hasn't interacted with
 *   - Missing consent: Displays names of blueprints that lack explicit consent
 * - Conditional action buttons based on validation status
 * - Responsive design for different screen sizes
 * - Internationalized content through vue-i18n
 *
 * Props:
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
 *
 * Behavior:
 * - If any blueprints lack consent, the "Continue Anyway" option is hidden
 * - User must go back and provide consent for all blueprints to proceed
 * - If only unattended uploaders exist, user can choose to continue anyway
 */

import { useI18n } from 'vue-i18n';
import {computed, onMounted, onUnmounted, ref, Ref, watch} from "vue";
const { t, locale } = useI18n();

const props = defineProps<{
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
}, { immediate: true });

/**
 * Hides the modal and emits the modalClosed event.
 * This allows the parent component to update its state accordingly.
 */
const hideModal = (): void => {
  modalVisible.value = false;
  emit('modalClosed');
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

  let combinedString: string = ' (';
  for (let i = 0; i < nStrings; i++) {
    combinedString += ('"' + strings[i] + '"');
    if (i < nStrings - 2) {
      combinedString += ', ';
    } else if (i === nStrings - 2) {
      combinedString += ', ';
    }
  }
  combinedString += ')';
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

    <div class="modal-backdrop" @click="hideModal"></div>

    <div
        class="issue-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        tabindex="-1"
    >
      <div class="modal-body d-flex flex-row align-items-center pt-5">
        <h2 id="modal-title" class="visually-hidden">{{ t("issue-modal.title") }}</h2>

        <div class="ps-2 pe-3 color-blue"><i class="bi bi-info-circle-fill fs-1"></i></div>

        <div>
          <div v-if="unattendedUploaderShare === 1">
            {{ t("issue-modal.none-attempted") }}
          </div>
          <div v-else-if="unattendedUploaderShare > 0">
            {{ t("issue-modal.not-all-attempted", {"skipped-uploads": combineStrings(props.unattendedUploaderNames)}) }}
          </div>

          <div v-if="blueprintsWithoutConsentCount > 0 && unattendedUploaderShare < 1">
            {{ t("issue-modal.not-all-consented", {"blueprints-wo-consent": combineStrings(props.blueprintsWithoutConsentNames)})  }}
          </div>
        </div>

      </div>

      <div class="modal-footer">
        <button
            type="button"
            class="btn btn-black"
            @click="hideModal"
        >
          {{ t("issue-modal.back") }}
        </button>

        <button
            v-if="canContinueAnyway"
            type="button"
            class="btn btn-light"
            @click="hideModal(); emit('continueAnyway')"
        >
          {{ t("issue-modal.continue-anyway") }}
        </button>
      </div>

    </div>
  </template>
</template>

<style scoped>
.issue-modal {
  background: white;
  z-index: 2000;
  position: fixed;
  top: 35%;
  margin-left: auto;
  margin-right: auto;
  left: 0;
  right: 0;
  width: 85%;
  border-radius: 5px;
}

.modal-backdrop {
  position: fixed;
  height: 100%;
  width: 100%;
  background: #959595;
  opacity: .75;
  z-index: 1000;
}

.btn-light {
  background: #e3e3e3;
}

.btn-light:hover {
  background: #dddddd;
}

.btn-black {
  background: #000000;
  border-color: #000000;
  color: #ffffff;
}

.btn-black:hover {
  background: #3b3b3b;
}

@media (min-width: 769px) {
  .issue-modal {
    width: 50%;
  }
}
</style>

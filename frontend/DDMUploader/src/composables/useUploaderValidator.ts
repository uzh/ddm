import {EXTRACTION_STATES} from "@uploader/utils/stateCatalog";
import {computed, ref, Ref} from "vue";
import {UploaderOutcome} from "@uploader/types/UploaderOutcome";

/**
 * useUploaderValidator
 *
 * A composable that validates uploader states and consent provisions.
 * It checks if all uploads have been attempted and if consent has been
 * obtained for all successfully extracted blueprints.
 *
 * @param uploaderOutcomes - Reactive reference to the uploader outcomes object
 *
 * @returns An object containing:
 *   - validateUploaders: Function to perform validation
 *   - unattendedUploaderShare: Percentage of uploaders not attempted
 *   - unattendedUploaderNames: Names of uploaders not attempted
 *   - blueprintsWithoutConsentCount: Number of blueprints missing consent
 *   - blueprintsWithoutConsentNames: Names of blueprints missing consent
 *   - allUploadersValid: Overall validation result
 */
export function useUploaderValidator(
  uploaderOutcomes: Ref<Record<number, UploaderOutcome>>
) {
  const unattendedUploaderNames: Ref<string[]> = ref([]);
  const blueprintsWithoutConsentNames: Ref<string[]> = ref([]);
  const blueprintsWithoutConsentCount: Ref<number> = ref(0);
  const allUploadersValid: Ref<boolean | null> = ref(null);

  const unattendedUploaderShare = computed(() => {
    const totalUploaders = Object.keys(uploaderOutcomes.value).length;
    if (totalUploaders === 0) return 0;

    const notAttemptedCount = unattendedUploaderNames.value.length;
    return notAttemptedCount / totalUploaders;
  })

  /**
   * Validates all uploaders to check for attempted uploads and consent.
   *
   * This function:
   * 1. Resets all validation indicators
   * 2. Checks if all uploads have been attempted
   * 3. Checks if consent has been provided for all successful extractions
   * 4. Updates the overall validation status
   *
   * @returns True if all uploaders are valid, false otherwise
   */
  function validateUploaders(): boolean {
    if (allDonationsAttempted() && consentObtainedForAll()) {
      allUploadersValid.value = true;
      return true;
    } else {
      allUploadersValid.value = false;
      return false;
    }
  }

  /**
   * Checks if all uploads have been attempted.
   *
   * An upload is considered "not attempted" if its state is still PENDING.
   * This function collects the names of unattended uploaders for display
   * in the UI.
   *
   * @returns True if all uploads have been attempted, false otherwise
   */
  const allDonationsAttempted = (): boolean => {
    unattendedUploaderNames.value = [];

    for (const uploader of Object.values(uploaderOutcomes.value)) {
      if (uploader.uploaderState === EXTRACTION_STATES.PENDING) {
        unattendedUploaderNames.value.push(uploader.uploaderName);
      }
    }
    return (unattendedUploaderNames.value.length === 0);
  }

  /**
   * Checks if consent has been provided for all successful extractions.
   *
   * For each successful blueprint extraction, this function verifies
   * that the user has explicitly provided consent (true or false).
   * Null consent values are considered invalid.
   *
   * @returns True if all successful extractions have consent, false otherwise
   */
  const consentObtainedForAll = (): boolean => {
    blueprintsWithoutConsentNames.value = [];
    blueprintsWithoutConsentCount.value = 0;

    for (const uploader of Object.values(uploaderOutcomes.value)) {

      if (!uploader.consentMap) {
        console.log(`Uploader ${uploader.uploaderName} is missing consentMap.`)
        continue;
      }

      for (const blueprint of Object.keys(uploader.consentMap)) {
        if (uploader.consentMap[blueprint] === null &&
            uploader.blueprintStates[blueprint].state === EXTRACTION_STATES.SUCCESS) {
          blueprintsWithoutConsentNames.value.push(uploader.blueprintNames[blueprint]);
          blueprintsWithoutConsentCount.value += 1;
        }
      }
    }
    return (blueprintsWithoutConsentNames.value.length === 0);
  }

  return {
    validateUploaders,
    unattendedUploaderShare,
    unattendedUploaderNames,
    blueprintsWithoutConsentCount,
    blueprintsWithoutConsentNames,
    allUploadersValid
  }
}

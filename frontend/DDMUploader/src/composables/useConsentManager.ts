import {ref, Ref} from "vue";
import {Blueprint} from "@uploader/types/Blueprint";

/**
 * Composable: useConsentManager
 *
 * Manages user consent for blueprint data extraction and submission.
 * Handles both individual blueprint consent and combined consent modes.
 *
 * Features:
 * - Initializes consent state for all blueprints
 * - Updates consent for individual blueprints or all blueprints at once
 * - Maintains reactive consent state
 *
 * @param blueprintConfigs - Array of blueprint configurations
 * @param combinedConsent - Whether to use combined consent mode (true) or per-blueprint consent (false)
 *
 * @returns {Object} An object containing:
 *   - blueprintConsentMap: Reactive map of blueprint IDs to consent status
 *   - updateConsent: Function to update consent state
 *
 * Usage:
 * ```
 * const { blueprintConsentMap, updateConsent } = useConsentManager(blueprints, true);
 *
 * // Update consent for all blueprints in combined mode
 * updateConsent(true, null);
 *
 * // Update consent for a specific blueprint
 * updateConsent(false, 123);
 * ```
 */
export function useConsentManager(
  blueprintConfigs: Blueprint[],
  combinedConsent: boolean
) {
  const blueprintConsentMap: Ref<Record<number, boolean | null>> = ref(initializeConsentMap());

  /**
   * Initializes the consent map with null values for all blueprints.
   *
   * @returns A record mapping blueprint IDs to initial consent values (null)
   */
  function initializeConsentMap(): Record<number, boolean | null> {
    const consentMap = {};
    for (const blueprint of blueprintConfigs) {
      consentMap[blueprint.id] = null;
    }
    return consentMap;
  }

  /**
   * Updates consent values in the blueprint consent map.
   *
   * In combined consent mode, this updates all blueprint consent values.
   * In individual consent mode, this updates only the specified blueprint.
   *
   * @param consent - The consent value to set (true for granted, false for denied)
   * @param blueprintId - The ID of the blueprint to update, or null for combined consent
   */
  const updateConsent = (consent: boolean, blueprintId: number | null): void => {
    if (combinedConsent) {
      for (const key of Object.keys(blueprintConsentMap.value)) {
        blueprintConsentMap.value[key] = consent;
      }
    } else {
      if (blueprintId === null) {
        console.warn('Attempted to update consent for null blueprintId in individual consent mode');
        return;
      }

      if (!(blueprintId in blueprintConsentMap.value)) {
        console.warn(`Attempted to update consent for unknown blueprint ID: ${blueprintId}`);
        return;
      }

      blueprintConsentMap.value[blueprintId] = consent;
    }
  }

  return {
    blueprintConsentMap,
    updateConsent
  }
}

import {ref, Ref} from 'vue';
import type {
  BlueprintDetailState,
  BlueprintExtractionStates,
  ExtractionStates,
} from '@uploader/types/ExtractionStates';
import {EXTRACTION_STATES} from "@uploader/utils/stateCatalog";
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";
import {ERROR_LEVELS, ProcessingError} from "@uploader/types/ProcessingError";

/**
 * useExtractionStateTracker
 *
 * A Vue composable that evaluates and tracks the state of data extraction processes.
 * It analyzes the success, failure, or partial completion of extraction operations
 * across multiple blueprints and provides a consolidated view of the extraction status.
 *
 * The composable handles:
 * - Tracking overall extraction state (success, partial, failed, no data)
 * - Monitoring individual blueprint extraction states
 * - Filtering and organizing critical errors for display
 * - Providing reactive state properties for UI components
 *
 * @param errors - Array of processing errors encountered during extraction
 * @param results - Object mapping blueprint IDs to their extraction outcomes
 *
 * @returns An object containing:
 *   - extractionState: Reactive reference to the overall extraction state
 *   - generalErrorsToDisplay: Reactive array of critical errors for display
 *   - blueprintExtractionStates: Reactive object with per-blueprint state details
 *   - getExtractionState: Function to evaluate and update extraction states
 */
export function useExtractionStateTracker(
  errors: ProcessingError[],
  results: Record<number,  BlueprintExtractionOutcome>
) {
  const extractionState: Ref<ExtractionStates> = ref(EXTRACTION_STATES.PENDING);
  const generalErrorsToDisplay: Ref<ProcessingError[]> = ref([]);
  const blueprintExtractionStates: Ref<BlueprintExtractionStates> = ref({});

  /**
   * Initializes the blueprint extraction states map with pending states.
   *
   * This function is called on composable creation to set up initial state
   * for all blueprints found in the results object.
   */
  function initialize(): void {
    for (const blueprintId of Object.keys(results)) {
      blueprintExtractionStates.value[blueprintId] = {state: EXTRACTION_STATES.PENDING, i18nState: null, errorsToDisplay: []};
    }
  }

  /**
   * Resets all state tracking to initial values.
   *
   * This function clears the current state before a new evaluation,
   * ensuring that old states don't affect new evaluations.
   */
  function resetState(): void {
    extractionState.value = EXTRACTION_STATES.PENDING;
    generalErrorsToDisplay.value = [];
    blueprintExtractionStates.value = {};
  }

  /**
   * Evaluates the final state of a processing session based on encountered errors and extraction results.
   *
   * This function coordinates the complete evaluation process by:
   * 1. Resetting the current state tracking
   * 2. Processing general critical errors
   * 3. Evaluating individual blueprint states
   * 4. Determining the overall extraction state
   *
   * This is the main entry point for state evaluation and should be called
   * whenever the underlying data changes.
   */
  function getExtractionState(): void {
    resetState();
    processGeneralErrors();
    evaluateBlueprintStates();
    evaluateOverallState()
  }

  /**
   * Identifies and collects critical errors from the general errors list.
   *
   * Critical errors at this level typically indicate issues that affected
   * the entire extraction process rather than specific blueprints.
   */
  function processGeneralErrors(): void {
    for (const error of errors) {
      if (error.level === ERROR_LEVELS.CRITICAL) {
        generalErrorsToDisplay.value.push(error);
      }
    }
  }

  /**
   * Evaluates the extraction state for each individual blueprint.
   *
   * Iterates through all blueprints in the results object and determines
   * their extraction state based on success, errors, and data presence.
   */
  function evaluateBlueprintStates(): void {
    for (const [blueprintId, result] of Object.entries(results)) {
      blueprintExtractionStates.value[blueprintId] = getBlueprintState(result);
    }
  }

  /**
   * Determines the overall extraction state based on blueprint states and general errors.
   *
   * This function synthesizes the individual blueprint states into a single
   * overall state that represents the extraction process as a whole.
   *
   * Priority order:
   * 1. If general critical errors exist, the state is FAILED
   * 2. Otherwise, determine state based on blueprint success/failure patterns
   */
  function evaluateOverallState(): void {
    if (generalErrorsToDisplay.value.length > 0) {
      extractionState.value = EXTRACTION_STATES.FAILED;
      return;
    }

    const nBlueprints = Object.keys(blueprintExtractionStates.value).length;
    const nSuccess = getStateCount(EXTRACTION_STATES.SUCCESS);
    const nNoData = getStateCount(EXTRACTION_STATES.NO_DATA);
    const nFailed = getStateCount(EXTRACTION_STATES.FAILED);

    extractionState.value = determineOverallState(nBlueprints, nSuccess, nNoData, nFailed);
  }

  /**
   * Calculates the overall state based on blueprint state counts.
   *
   * @param total - Total number of blueprints
   * @param success - Number of blueprints with successful extraction
   * @param noData - Number of blueprints with no extracted data
   * @param failed - Number of blueprints with extraction failures
   * @returns The appropriate overall extraction state
   */
  function determineOverallState(
    total: number,
    success: number,
    noData: number,
    failed:number
  ): ExtractionStates {
    if (success === total) return EXTRACTION_STATES.SUCCESS;
    if (noData === total) return EXTRACTION_STATES.NO_DATA;
    if (failed === total) return EXTRACTION_STATES.FAILED;
    return EXTRACTION_STATES.PARTIAL;
  }

  /**
   * Analyzes a single blueprint's extraction result to determine its state.
   *
   * This function performs a detailed analysis of a blueprint's extraction outcome by:
   * - Checking for critical errors during extraction
   * - Evaluating the amount of data successfully extracted
   * - Analyzing why data might be missing (missing fields, filtering, etc.)
   *
   * Based on this analysis, it determines the appropriate state and provides
   * internationalization keys for user-facing messages.
   *
   * @param blueprintOutcome - The extraction outcome object to analyze
   * @returns A BlueprintDetailState object with state, i18n key, and errors
   */
  function getBlueprintState(blueprintOutcome: BlueprintExtractionOutcome): BlueprintDetailState {
    let state: ExtractionStates = EXTRACTION_STATES.PENDING;
    let i18nState: string | null = null;
    const criticalErrors = blueprintOutcome.processingErrors.filter(error => error.level === ERROR_LEVELS.CRITICAL);

    if (criticalErrors.length > 0) {
      state = EXTRACTION_STATES.FAILED;
      i18nState = 'extraction-state.blueprint.failed';
    }

    // Evaluate extraction state.
    const nExtracted = blueprintOutcome.extractedData.length;

    const stats = blueprintOutcome.extractionStats;
    const ratioMissing = stats.nRowsTotal > 0
      ? stats.nRowsMissingField / stats.nRowsTotal
      : 0;
    const ratioFilteredOut = stats.nRowsTotal > 0
      ? stats.nRowsFilteredOut / stats.nRowsTotal
      : 0;

    if (nExtracted === 0 && criticalErrors.length === 0) {
      state = EXTRACTION_STATES.NO_DATA;
      if (ratioMissing === 1) {
        i18nState = 'extraction-state.blueprint.all-missing-fields';
      } else if (ratioFilteredOut === 1) {
        i18nState = 'extraction-state.blueprint.all-filtered-out';
      } else {
        i18nState = 'extraction-state.blueprint.no-data-extracted';
      }
    } else if (criticalErrors.length === 0) {
      state = EXTRACTION_STATES.SUCCESS;
      i18nState = 'extraction-state.blueprint.success'
    }

    return {state: state, i18nState: i18nState, errorsToDisplay: criticalErrors} as BlueprintDetailState;
  }

  /**
   * Counts how many blueprints have a specific extraction state.
   *
   * This helper function is used to calculate how many blueprints
   * succeeded, failed, or had no data, which is needed to determine
   * the overall extraction state.
   *
   * @param targetState - The extraction state to count
   * @returns The number of blueprints with the specified state
   */
  function getStateCount(targetState: ExtractionStates): number {
    return Object.values(blueprintExtractionStates.value)
      .filter(state => state.state === targetState)
      .length;
  }

  initialize();

  return {
    extractionState,
    generalErrorsToDisplay,
    blueprintExtractionStates,
    getExtractionState
  }
}

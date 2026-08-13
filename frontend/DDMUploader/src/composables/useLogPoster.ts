import {useTranslation} from "@uploader/composables/useTranslation";
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";
import {ref, Ref} from "vue";
import {ProcessingError} from "@uploader/types/ProcessingError";

/**
 * useLogPoster
 *
 * Posts structured logs (errors, extraction stats, rule usage, field
 * mappings) for a processing session to the backend, sharing one timestamp
 * per batch for correlation. Network failures are logged to the console,
 * not thrown.
 *
 * @param uploaderId - Unique identifier for the uploader component
 * @param exceptionUrl - Backend endpoint URL for log submission
 *
 * @returns { postLogs } - Function to submit all logs for a processing session
 */
export function useLogPoster(
  uploaderId: number,
  exceptionUrl: string
) {
  const { t } = useTranslation({locale: 'en'});
  let logDate: Ref<number> = ref(Date.now());

  /**
   * Posts all processing logs and statistics to the backend.
   *
   * This function:
   * 1. Captures a unified timestamp for all logs in this batch
   * 2. Posts general processing errors (not blueprint-specific)
   * 3. Posts blueprint-specific errors with translations
   * 4. Posts extraction statistics, rule usage logs, and field mappings
   *
   * All logs are posted individually but share the same timestamp for correlation.
   * Network failures are logged to the console but do not cause the function to fail.
   *
   * @param generalErrors - Array of general processing errors
   * @param blueprintOutcomeMap - Map of blueprint IDs to their extraction outcomes
   * @returns A Promise that resolves when all logs have been posted
   */
  async function postLogs(
    generalErrors: ProcessingError[],
    blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>
  ): Promise<void> {
    // Take a timestamp that is the same for all.
    logDate.value = Date.now();

    // Log general errors.
    for (const error of generalErrors) {
      await postLog(null, error.type, t(error.i18nDetail, error.context));
    }

    // Log blueprint errors.
    for (const blueprintOutcome of Object.values(blueprintOutcomeMap)) {
      for (const error of blueprintOutcome.processingErrors) {
        if (error.type === 'NO_FILE_MATCH') {
          await postLog(blueprintOutcome.blueprintId, error.type, t(`${error.i18nDetail}-detail`, error.context));
        } else {
          await postLog(blueprintOutcome.blueprintId, error.type, t(error.i18nDetail, error.context));
        }
      }

      const logsToPost = {
        'EXTRACTION_STATS': blueprintOutcome.extractionStats,
        'EXTRACTION_LOG': blueprintOutcome.extractionRuleLog,
        'EXTRACTED_FIELDS_MAP': blueprintOutcome.extractedFieldsMap
      };
      for (const [type, data] of Object.entries(logsToPost)) {
        await postLog(blueprintOutcome.blueprintId, type, JSON.stringify(data));
      }
    }
  }

  async function postLog(
    blueprintId: number | null,
    logType: string,
    message: string,
  ): Promise<boolean> {
    const postData = {
      'status_code': logType,
      'message': message,
      'raised_by': 'client',
      'uploader': uploaderId,
      'blueprint': blueprintId,
      'date': new Date(logDate.value).toISOString()
    }
    try {
      const response = await fetch(exceptionUrl, {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
      });

      if (!response.ok) {
        console.error(`Error posting log: ${response.status} ${response.statusText}`);
        return false;
      }

      return true;
    } catch (error) {
      console.error("Could not post error message:", error);
      return false;
    }
  }

  return {
    postLogs
  }
}

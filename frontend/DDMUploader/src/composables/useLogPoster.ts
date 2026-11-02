import {useTranslation} from "@uploader/composables/useTranslation";
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";
import {ref, Ref} from "vue";
import {ProcessingError} from "@uploader/types/ProcessingError";

type LogEntryPayload = {
  status_code: string,
  message: string,
  uploader: number,
  blueprint: number | null,
};

type LogBundlePayload = {
  date: string,
  logs: LogEntryPayload[],
};

const MAX_ATTEMPTS = 3;       // 1 initial attempt + 2 retries
const RETRY_DELAY_MS = 500;   // fixed delay, no backoff

/**
 * useLogPoster
 *
 * Posts structured logs (errors, extraction stats, rule usage, field
 * mappings) for a processing session to the backend, bundled into a
 * single request sharing one timestamp for correlation. Network failures
 * are retried a couple of times, then logged to the console - never
 * thrown.
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
   * Posts all processing logs and statistics to the backend as one
   * bundled request.
   *
   * This function:
   * 1. Captures a unified timestamp for all logs in this batch
   * 2. Collects general processing errors (not blueprint-specific)
   * 3. Collects blueprint-specific errors with translations
   * 4. Collects extraction statistics, rule usage logs, and field mappings
   * 5. Posts everything collected in one request (no-op if there's nothing
   *    to log)
   *
   * Network failures are retried a couple of times, then logged to the
   * console; this function never rejects.
   *
   * @param generalErrors - Array of general processing errors
   * @param blueprintOutcomeMap - Map of blueprint IDs to their extraction outcomes
   * @returns A Promise that resolves once posting has been attempted
   */
  async function postLogs(
    generalErrors: ProcessingError[],
    blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>
  ): Promise<void> {
    // Take a timestamp that is the same for all.
    logDate.value = Date.now();

    const logs: LogEntryPayload[] = [];

    // Collect general errors.
    for (const error of generalErrors) {
      if (error.type === 'ZIP_READ_FAIL') {
        // Post the structured context (underlying reader error, nested-zip
        // path/depth) rather than the generic participant-facing sentence.
        logs.push(buildLogEntry(null, error.type, JSON.stringify(error.context)));
      } else {
        logs.push(buildLogEntry(null, error.type, t(error.i18nDetail, error.context)));
      }
    }

    // Collect blueprint errors.
    for (const blueprintOutcome of Object.values(blueprintOutcomeMap)) {
      for (const error of blueprintOutcome.processingErrors) {
        if (error.type === 'NO_FILE_MATCH') {
          logs.push(buildLogEntry(blueprintOutcome.blueprintId, error.type, t(`${error.i18nDetail}-detail`, error.context)));
        } else {
          logs.push(buildLogEntry(blueprintOutcome.blueprintId, error.type, t(error.i18nDetail, error.context)));
        }
      }

      const logsToPost = {
        'EXTRACTION_STATS': blueprintOutcome.extractionStats,
        'EXTRACTION_LOG': blueprintOutcome.extractionRuleLog,
        'EXTRACTED_FIELDS_MAP': Object.fromEntries(blueprintOutcome.extractedFieldsMap)
      };
      for (const [type, data] of Object.entries(logsToPost)) {
        logs.push(buildLogEntry(blueprintOutcome.blueprintId, type, JSON.stringify(data)));
      }
    }

    if (logs.length === 0) {
      return;
    }

    await postBundle({
      date: new Date(logDate.value).toISOString(),
      logs,
    });
  }

  function buildLogEntry(
    blueprintId: number | null,
    logType: string,
    message: string,
  ): LogEntryPayload {
    return {
      status_code: logType,
      message: message,
      uploader: uploaderId,
      blueprint: blueprintId,
    };
  }

  async function postBundle(payload: LogBundlePayload): Promise<void> {
    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
      try {
        const response = await fetch(exceptionUrl, {
          method: "POST",
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          return;
        }

        console.error(`Error posting logs: ${response.status} ${response.statusText}`);
      } catch (error) {
        console.error("Could not post logs:", error);
      }

      if (attempt < MAX_ATTEMPTS) {
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY_MS));
      }
    }
    // All attempts exhausted - already logged above; swallow and return
    // normally so postLogs() never rejects.
  }

  return {
    postLogs
  }
}

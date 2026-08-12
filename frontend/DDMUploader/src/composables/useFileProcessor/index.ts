import { reactive } from 'vue';
import { BlueprintExtractionOutcome } from "@uploader/classes/BlueprintExtractionOutcome"
import {ProcessingError} from "@uploader/types/ProcessingError";
import {handleSingleFile, handleZipFile} from "@uploader/composables/useFileProcessor/fileHandlers";

/**
 * useFileProcessor
 *
 * Main entry point for processing a user-selected file (JSON/CSV/TXT, as a
 * single file or a ZIP archive) against blueprint configurations. For ZIP
 * archives, if a blueprint's parser fails to extract data, its backup
 * blueprints (in priority order) are tried instead. Results and errors are
 * written into reactive state.
 *
 * @param expectsZip - Whether to process input as a ZIP archive (true) or single file (false)
 * @param blueprints - Array of blueprint configurations defining extraction rules and formats
 * @param nestedZipExtractionDepth - How many levels deep to extract zip files within zip files (0 = no nested extraction)
 *
 * @returns
 *   - handleSelectedFile: Function to process a user-selected file
 *   - blueprintOutcomeMap: Reactive map of blueprint outcomes indexed by blueprint ID
 *   - generalErrors: Reactive array of general processing errors
 */
export function useFileProcessor(
  expectsZip: boolean,
  blueprints: any[],
  nestedZipExtractionDepth: number = 0,
) {

  const generalErrors = reactive<ProcessingError[]>([]);  // Used to track general errors.
  const blueprintOutcomeMap = reactive<Record<number, BlueprintExtractionOutcome>>({});

  function resetState(): void {
    generalErrors.length = 0;

    Object.keys(blueprintOutcomeMap).forEach(key => {
      delete blueprintOutcomeMap[key];
    });

    for (const blueprint of blueprints) {
      blueprintOutcomeMap[blueprint.id] = new BlueprintExtractionOutcome(blueprint);
    }
  }

  function initialize(): void {
    resetState();
  }

  /**
   * Processes a user-selected file based on the configured expectations.
   *
   * This function:
   * 1. Resets the current state and errors
   * 2. Updates the processor status to 'processing'
   * 3. Applies a small delay for UI responsiveness (optional)
   * 4. Dispatches the file to the appropriate handler based on type
   * 5. Updates the processor status to 'done' when complete
   *
   * All processing results and errors are stored in the reactive state
   * objects (blueprintOutcomeMap and generalErrors).
   *
   * @param file - The File object to process (from file input or drop event)
   * @returns A Promise that resolves when processing is complete
   */
  async function handleSelectedFile(file: File): Promise<void> {
    resetState();

    try {
      await new Promise<void>(resolve => setTimeout(resolve, 1000));

      if (expectsZip) {
        await handleZipFile(file, blueprints, blueprintOutcomeMap, generalErrors, nestedZipExtractionDepth);
      } else {
        await handleSingleFile(file, blueprints, blueprintOutcomeMap, generalErrors);
      }
    } catch (error) {
      console.error("Unexpected error during file processing:", error);
    }

    return;
  }

  initialize();

  return {
    generalErrors,
    blueprintOutcomeMap,
    handleSelectedFile
  }
}

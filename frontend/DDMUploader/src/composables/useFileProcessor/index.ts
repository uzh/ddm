import { reactive } from 'vue';
import { BlueprintExtractionOutcome } from "@uploader/classes/BlueprintExtractionOutcome"
import {ProcessingError} from "@uploader/types/ProcessingError";
import {handleSingleFile, handleZipFile} from "@uploader/composables/useFileProcessor/fileHandlers";

/**
 * useFileProcessor
 *
 * A Vue composable that handles file processing and data extraction based on blueprint configurations.
 * It serves as the main entry point for the file processing system, managing state and coordinating
 * specialized processing modules.
 *
 * Features:
 * - Processes both single files (JSON/CSV) and ZIP archives
 * - Tracks extraction results and errors in reactive state objects
 * - Coordinates the complete processing pipeline:
 *   1. File validation and reading
 *   2. Content parsing and structure extraction
 *   3. Rule application and data transformation
 *   4. Result aggregation and error tracking
 *
 * @param expectsZip - Whether to process input as a ZIP archive (true) or single file (false)
 * @param blueprints - Array of blueprint configurations defining extraction rules and formats
 *
 * @returns An object containing:
 *   - handleSelectedFile: Function to process a user-selected file
 *   - blueprintOutcomeMap: Reactive map of blueprint outcomes indexed by blueprint ID
 *   - generalErrors: Reactive array of general processing errors
 *   - processorStatus: Reactive object tracking the current processing state
 *   - progress: Reactive object tracking processing progress (0-100)
 *
 * Usage:
 * ```typescript
 * const { handleSelectedFile, blueprintOutcomeMap, generalErrors } = useFileProcessor(true, blueprints);
 *
 * // Process a file
 * await handleSelectedFile(fileObject);
 *
 * // Access extraction results
 * console.log(blueprintOutcomeMap[blueprintId].extractedData);
 * ```
 */
export function useFileProcessor(
  expectsZip: boolean,
  blueprints: any[]
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
        await handleZipFile(file, blueprints, blueprintOutcomeMap, generalErrors);
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

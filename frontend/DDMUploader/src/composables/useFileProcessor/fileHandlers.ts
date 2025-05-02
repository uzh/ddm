import JSZip from 'jszip';
import {ERROR_CATALOG} from "@uploader/utils/errorCatalog";
import {registerGeneralError} from "@uploader/composables/useFileProcessor/errorHandling";
import {Blueprint} from "@uploader/types/Blueprint";
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";
import {ProcessingError} from "@uploader/types/ProcessingError";
import {processContent} from "@uploader/composables/useFileProcessor/contentParsers";

/**
 * Processes a ZIP archive by extracting and processing matching files.
 *
 * This function:
 * 1. Validates that the file is a valid ZIP archive
 * 2. Extracts the archive contents
 * 3. For each blueprint:
 *    - Compiles the regex pattern for file matching
 *    - Finds matching files within the archive
 *    - Extracts and processes each matching file
 * 4. Records all errors and processing results
 *
 * If a blueprint has no matching files or encounters errors, appropriate
 * error messages are recorded in the blueprint's outcome.
 *
 * @param file - The ZIP file to process
 * @param blueprints - Blueprint configurations defining extraction rules
 * @param blueprintOutcomeMap - Map to store extraction results by blueprint ID
 * @param generalErrors - Collection for recording general processing errors
 * @returns A Promise that resolves when processing is complete
 */
export async function handleZipFile(
  file: File,
  blueprints: Blueprint[],
  blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>,
  generalErrors: ProcessingError[]
): Promise<void> {
  // Validate file.
  if (!fileIsZip(file)) {
    const fileType = file.name.slice(file.name.lastIndexOf('.') + 1);
    registerGeneralError(generalErrors, ERROR_CATALOG.INVALID_ZIP, {fileType: fileType});
    return;
  }

  let zip: JSZip;

  try {
    zip = await JSZip.loadAsync(file);
  } catch (error) {
    registerGeneralError(generalErrors, ERROR_CATALOG.ZIP_READ_FAIL, {error: error});
    return;
  }

  for (const blueprint of blueprints) {
    let re: RegExp;
    try {
      re = new RegExp(blueprint.regex_path);
    } catch (error) {
      blueprintOutcomeMap[blueprint.id].registerError(ERROR_CATALOG.INVALID_REGEX, {error: error});
      continue;
    }

    const matchingFiles = zip.file(re);
    if (matchingFiles.length === 0) {
      const availableFiles = Object.keys(zip.files);
      const errorContext = { regexPath: blueprint.regex_path, availableFiles: availableFiles }
      blueprintOutcomeMap[blueprint.id].registerError(ERROR_CATALOG.NO_FILE_MATCH, errorContext);
      continue;
    }

    for (const zipEntry of matchingFiles) {
      try {
        const content = await zipEntry.async("string");
        processContent(content, blueprint, blueprintOutcomeMap);
      } catch (error) {
        blueprintOutcomeMap[blueprint.id].registerError(ERROR_CATALOG.FILE_PROCESSING_FAIL_GENERAL, {error: error});
      }
    }
  }
}

/**
 * Handles the processing of a single file.
 *
 * Reads the file as plain text using FileReader, then applies all available blueprints
 * by passing the content through `processContent()`. Results are stored in `blueprintResultMap`.
 *
 * @param file - The selected file to process (expected to be text-based like JSON or CSV).
 * @param blueprints - An array of blueprint configurations defining format, fields, and extraction rules.
 * @param blueprintOutcomeMap - A map of blueprint ids to their extraction outcome.
 * @param generalErrors - The array where general errors are registered.
 */
export function handleSingleFile(
  file: File,
  blueprints: Blueprint[],
  blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>,
  generalErrors: ProcessingError[]
): Promise<void> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = function(event: ProgressEvent<FileReader>) {
      const content = event.target.result;
      if (typeof content !== 'string') {
        registerGeneralError(generalErrors, ERROR_CATALOG.STRING_CONVERSION_ERROR, {});
        return reject('invalid content');
      }

      blueprints.forEach(blueprint => {
        try {
          processContent(content, blueprint, blueprintOutcomeMap);
        } catch (error) {
          blueprintOutcomeMap[blueprint.id].registerError(ERROR_CATALOG.FILE_PROCESSING_FAIL_GENERAL, {error: error});
        }
      });
      resolve();
    }

    reader.onerror = function(event: ProgressEvent<FileReader>) {
      const error = event.target?.error || new Error('Unknown file reading error');
      registerGeneralError(generalErrors, ERROR_CATALOG.FILE_PROCESSING_FAIL_GENERAL, {error: error});
      reject(error);
    };

    reader.readAsText(file);
  });
}

/**
 * Determines whether a file is a valid ZIP archive.
 *
 * Performs validation based on:
 * 1. File extension (.zip)
 * 2. MIME type (application/zip and related types)
 *
 * This function helps prevent processing non-ZIP files that could
 * cause errors during extraction.
 *
 * @param file - The file to validate
 * @returns True if the file appears to be a valid ZIP archive, false otherwise
 */
export function fileIsZip(file: File): boolean {
  const extensionIsValid = file.name.toLowerCase().endsWith('.zip');
  const mimeIsValid = [
      'application/zip',
      'application/x-zip-compressed',
      'multipart/x-zip'
  ].includes(file.type);
  return extensionIsValid && mimeIsValid;
}

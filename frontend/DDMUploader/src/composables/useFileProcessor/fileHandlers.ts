import JSZip from 'jszip';
import {ERROR_CATALOG} from "@uploader/utils/errorCatalog";
import {registerGeneralError} from "@uploader/composables/useFileProcessor/errorHandling";
import {Blueprint} from "@uploader/types/Blueprint";
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";
import {BlueprintFilePath} from "@uploader/types/BlueprintFilePath";
import {ProcessingError} from "@uploader/types/ProcessingError";
import {processContent} from "@uploader/composables/useFileProcessor/contentParsers";


type ExtractedZipFile = {
  fullPath: string;
  entry: JSZip.JSZipObject;
};

/**
 * Normalizes a file path by removing leading './' and converting
 * backslashes to forward slashes for cross-platform consistency.
 */
function normalizePath(path: string): string {
  return path.replace(/^\.\/+/, '').replace(/\\/g, '/');
}

/**
 * Strips a leading UTF-8 byte-order-mark (BOM, U+FEFF) from file content,
 * if present. Some editors/export tools prepend one when saving text as
 * UTF-8; left in place, it makes JSON.parse (and PapaParse/plain-text
 * key/value splitting) fail on the very first character even though the
 * rest of the content is perfectly valid.
 */
function stripBom(content: string): string {
  return content.charCodeAt(0) === 0xfeff ? content.slice(1) : content;
}

/**
 * True if a zip entry path is inside a top-level `__MACOSX/` directory --
 * added automatically by macOS's Archive Utility/Finder/`zip` to hold
 * AppleDouble resource-fork sidecar files, and never real user data. Safe
 * to drop unconditionally: no legitimate export tool uses this exact
 * directory name.
 */
function isInMacosMetadataDir(rawPath: string): boolean {
  return normalizePath(rawPath).split('/').filter(Boolean)[0] === '__MACOSX';
}

/**
 * Removes AppleDouble resource-fork sidecar files (named `._<filename>`)
 * that macOS's `zip`/Archive Utility can place directly alongside the real
 * file (i.e. outside `__MACOSX/`, where `isInMacosMetadataDir` alone
 * wouldn't catch them). Critically, a `._conversations.json` sidecar has
 * the same suffix as (and can therefore be accidentally matched by a
 * literal/suffix BlueprintFilePath pattern for) the real `conversations.json`,
 * while its content is opaque binary metadata that will always fail to parse.
 *
 * Only removed when a real sibling file (same directory, same name minus
 * the `._` prefix) is also present -- that pairing is the actual signature
 * of an AppleDouble sidecar. A file that happens to be named `._something`
 * with no such sibling is left alone, since it's then indistinguishable
 * from a genuine, deliberately-named user file.
 */
export function stripAppleDoubleSidecars(entries: ExtractedZipFile[]): ExtractedZipFile[] {
  const allPaths = new Set(entries.map(e => e.fullPath));

  return entries.filter(({fullPath}) => {
    const segments = fullPath.split('/');
    const basename = segments[segments.length - 1];
    if (!basename.startsWith('._')) return true;

    const siblingPath = [...segments.slice(0, -1), basename.slice(2)].join('/');
    return !allPaths.has(siblingPath);
  });
}

/**
 * Recursively collects all file entries from a ZIP archive, including nested ZIPs.
 *
 * This function traverses a ZIP archive and extracts metadata for all files,
 * building full paths that reflect the archive structure. When nested ZIP files
 * are encountered, they are recursively processed up to MAX_NESTED_ZIP_DEPTH (3),
 * with their contents included in the returned entries.
 *
 * @param zip - The JSZip instance to collect entries from
 * @param generalErrors - Array to record any errors encountered during processing
 * @param maxDepth - How many levels deep to extract zip files within zip files (0 = no nested extraction)
 * @param depth - Current nesting depth (used internally for recursion limiting)
 * @param parentPath - Path prefix from parent archives (used internally for nested ZIPs)
 * @returns Promise resolving to an array of ExtractedZipFile objects, each containing
 *          the full path (including nested archive paths) and the JSZip entry object
 *
 * @example
 * // For a ZIP with structure:
 * // - data.json
 * // - nested.zip
 * //   - inner.json
 * //
 * // Returns entries with fullPath values:
 * // - "data.json"
 * // - "nested.zip/inner.json"
 */
export async function collectZipEntries(
  zip: JSZip,
  generalErrors: ProcessingError[],
  maxDepth: number,
  depth: number = 0,
  parentPath: string = ''
): Promise<ExtractedZipFile[]> {
  const entries: ExtractedZipFile[] = [];

  for (const entry of Object.values(zip.files)) {
    if (entry.dir) {
      continue;
    }

    if (isInMacosMetadataDir(entry.name)) {
      continue;
    }

    const normalizedPath = normalizePath(entry.name);
    const normalizedName = normalizedPath.split('/').filter(Boolean).pop();

    const entryPath = parentPath
      ? `${parentPath}/${normalizedName}`
      : normalizedName;

    if (entry.name.toLowerCase().endsWith('.zip') && depth < maxDepth) {
      try {
        const nestedBuffer = await entry.async('arraybuffer');
        const nestedZip = await JSZip.loadAsync(nestedBuffer);

        // Use the ZIP's actual filename as the prefix
        const nestedParent = parentPath
          ? `${parentPath}/${normalizedName}`
          : normalizedName;

        const nestedEntries = await collectZipEntries(
          nestedZip,
          generalErrors,
          maxDepth,
          depth + 1,
          nestedParent.replace(/\.zip$/i, '.zip')
        );

        entries.push(...nestedEntries);
        continue;
      } catch (error) {
        registerGeneralError(generalErrors, ERROR_CATALOG.ZIP_READ_FAIL, { error });
      }
    }

    entries.push({ fullPath: entryPath, entry });
  }

  return entries;
}

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
 * @param nestedZipExtractionDepth - How many levels deep to extract zip files within zip files (0 = no nested extraction)
 * @returns A Promise that resolves when processing is complete
 */
export async function handleZipFile(
  file: File,
  blueprints: Blueprint[],
  blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>,
  generalErrors: ProcessingError[],
  nestedZipExtractionDepth: number,
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

  const extractedFiles = stripAppleDoubleSidecars(
    await collectZipEntries(zip, generalErrors, nestedZipExtractionDepth)
  );
  const availableFiles = Array.from(new Set(extractedFiles.map(entry => entry.fullPath)));

  const blueprintLookup = new Map(blueprints.map(bp => [bp.id, bp]));
  const blueprintsToProcess = blueprints.filter(bp => !bp.is_backup);

  for (const blueprint of blueprintsToProcess) {
    let succeeded = false;

    const matchedFilePaths = matchFilePaths(availableFiles, blueprint.file_paths, blueprint.id, blueprintOutcomeMap);
    if (matchedFilePaths.length === 0) {
      const errorContext = { regexPath: blueprint.file_paths, availableFiles: availableFiles }
      blueprintOutcomeMap[blueprint.id].registerError(ERROR_CATALOG.NO_FILE_MATCH, errorContext);
    } else {
      for (const zipPath of matchedFilePaths) {
        try {
          const zipEntry = extractedFiles.find(f => f.fullPath === zipPath);
          const content = stripBom(await zipEntry.entry.async("string"));
          processContent(content, blueprint, blueprintOutcomeMap);
          succeeded = true;
        } catch (error) {
          blueprintOutcomeMap[blueprint.id].registerError(ERROR_CATALOG.FILE_PROCESSING_FAIL_GENERAL, {error: error});
        }
      }
    }

    if (!succeeded) {
      addBackupBlueprint(blueprint, blueprintsToProcess, blueprintLookup);
    }
  }
}

function addBackupBlueprint(
  blueprint: Blueprint,
  blueprintList: Blueprint[],
  blueprintLookup: Map<number, Blueprint>
) {
  if (blueprint.is_backup) return;

  for (const backupId of blueprint.backup_ids ?? []) {
    const backupBlueprint = blueprintLookup.get(backupId);
    if (backupBlueprint && !blueprintList.includes(backupBlueprint)) {
      blueprintList.push(backupBlueprint);
    }
  }
}

/**
 * Finds all files in a ZIP archive that matches any of the blueprint's file paths.
 *
 * Searches through the blueprint's file paths in priority order and returns all the
 * matching files found in the ZIP archive. File paths can be:
 * - Literal paths for exact right-hand-side matching (e.g., "data/report.csv" matches "some_folder/data/report.csv")
 * - Regex patterns
 *
 * The function filters out directories and only matches against actual files.
 * If a regex pattern is invalid, an error is recorded in the blueprint outcome
 * and the next file path is tried.
 *
 * @param zipPaths - A list of available zip paths
 * @param blueprintFilePaths - List of configured blueprint file paths
 * @param blueprintId - ID of Blueprint
 * @param blueprintOutcomeMap - Map for recording regex parsing errors
 * @returns The matched file paths within the ZIP, or null if no match found
 */
export function matchFilePaths(
  zipPaths: string[],
  blueprintFilePaths: BlueprintFilePath[],
  blueprintId: number,
  blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>
): string[] {

  for (const filePath of blueprintFilePaths) {
    let path: string | RegExp;
    if (filePath.is_regex) {
      // Ensure regex file path is correct RegExp
      try {
        path = new RegExp(filePath.path);
      } catch (error) {
        blueprintOutcomeMap[blueprintId].registerError(ERROR_CATALOG.INVALID_REGEX, {error: error});
        continue;
      }
    } else {
      path = filePath.path;
    }

    let matchedPaths: string[] = [];
    for (const zipPath of zipPaths) {
      if (path instanceof RegExp) {
        if ((path).test(zipPath)) {
          matchedPaths.push(zipPath);
        }

      } else {
        if (zipPath.endsWith(path)) {
          matchedPaths.push(zipPath);
        }
      }
    }

    if (matchedPaths.length > 0) {
      return matchedPaths;
    }
  }
  return [];
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
      const rawContent = event.target.result;
      if (typeof rawContent !== 'string') {
        registerGeneralError(generalErrors, ERROR_CATALOG.STRING_CONVERSION_ERROR, {});
        return reject('invalid content');
      }
      const content = stripBom(rawContent);

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

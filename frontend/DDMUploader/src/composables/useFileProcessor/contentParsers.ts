import Papa from "papaparse";
import {ERROR_CATALOG} from "@uploader/utils/errorCatalog";
import {Blueprint} from "@uploader/types/Blueprint";
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";
import {extractData, getKeyMap, getMissingFields} from "@uploader/composables/useFileProcessor/extractionEngine";

/**
 * Processes a single file's content using a provided blueprint definition.
 *
 * This includes:
 * - Parsing the file content based on the format (JSON or CSV)
 * - Validating expected fields
 * - Applying extraction rules (with optional regex matching)
 * - Tracking errors, filtered rows, and stats in a structured result
 *
 * @param content - Raw file content as a string.
 * @param blueprint - The blueprint configuration defining format, fields, and extraction rules.
 * @param blueprintOutcomeMap - A map of blueprint ids to their extraction outcome.
 * @returns void — results are written directly to blueprintResultMap[blueprint.id]
 */
export function processContent(
  content: string,
  blueprint: Blueprint,
  blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>
): void {
  // Exit early, if no extraction rules are defined.
  if (blueprint.extraction_rules.length === 0) {
    blueprintOutcomeMap[blueprint.id].registerError(ERROR_CATALOG.NO_EXTRACTION_RULES, {});
    return;
  }
  const parsedContentArray = getParsedContentArray(content, blueprint, blueprintOutcomeMap);

  if (!parsedContentArray) {
    blueprintOutcomeMap[blueprint.id].registerError(ERROR_CATALOG.PARSING_ERROR, {contentType: ''});
    return;
  }
  blueprintOutcomeMap[blueprint.id].extractionStats.nRowsTotal = parsedContentArray.length;

  for (const dataRow of parsedContentArray) {
    // Skipp row if is null/undefined
    if (dataRow == null) {
      continue
    }

    // Validate fields.
    const missingFields = getMissingFields(
      dataRow,
      blueprint.expected_fields,
      blueprint.exp_fields_regex_matching
    );

    if (missingFields.length > 0) {
      blueprintOutcomeMap[blueprint.id].extractionStats.nRowsMissingField += 1;
      continue;
    }

    // Construct key map and extract data.
    const keyMap = getKeyMap(dataRow, blueprint.extraction_rules, blueprint.id, blueprintOutcomeMap);
    extractData(dataRow, blueprint.extraction_rules, keyMap, blueprint.id, blueprintOutcomeMap);
  }
}

/**
 * Parses raw content into an array of entries based on the specified format.
 *
 * Supports JSON and CSV formats. Optionally applies a JSON extraction root
 * or a custom CSV delimiter if provided.
 *
 * @param content - Raw file content as a string
 * @param blueprint - A blueprint configuration.
 * @param blueprintOutcomeMap - A map of blueprint ids to their extraction outcome.
 * @returns An array of parsed content entries
 * @throws If the content could not be parsed or format is unsupported
 */
export function getParsedContentArray(
  content,
  blueprint: Blueprint,
  blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>
): any[] | null {
  let parsedContentArray: any[] | null = null;

  if (blueprint.format === 'json') {
    try {
      parsedContentArray = loadJsonContent(content, blueprint.json_extraction_root);
    } catch (error) {
      blueprintOutcomeMap[blueprint.id].registerError(ERROR_CATALOG.PARSING_ERROR, {contentType: 'JSON', error: error});
    }
  }
  else if (blueprint.format === 'csv') {
    try {
      parsedContentArray = loadCsvContent(content, blueprint.csv_delimiter);
    } catch (error) {
      blueprintOutcomeMap[blueprint.id].registerError(ERROR_CATALOG.PARSING_ERROR, {contentType: 'CSV', error: error});
    }
  } else {
    blueprintOutcomeMap[blueprint.id].registerError(ERROR_CATALOG.UNSUPPORTED_BP_FORMAT, {format: blueprint.format});
    return null;
  }

  if (!parsedContentArray){
    blueprintOutcomeMap[blueprint.id].registerError(ERROR_CATALOG.PARSING_ERROR, {contentType: blueprint.format});
    return null;
  }
  return parsedContentArray;
}

interface ParsedData {
  [key: string]: any;
}

/**
 * Parses JSON content and extracts a nested structure based on a given extraction root path.
 *
 * The function attempts to parse the input string as JSON. If an `extractionRoot` is provided,
 * it navigates the parsed object to retrieve a nested value (using dot/bracket notation).
 * If the final result is not iterable (i.e., not an array or similar), it is wrapped in an array.
 *
 * Errors encountered during parsing or extraction are pushed to the `generalErrors` array.
 *
 * @param {string} content - Raw JSON content as a string.
 * @param {string} extractionRoot - Dot/bracket path to the desired nested value.
 * @returns {Array|null} - An array of extracted entries, or null if parsing or extraction fails.
 */
export function loadJsonContent(
  content: string,
  extractionRoot: string
): ParsedData[] | null {
  let fileContent: any;

  try {
    fileContent = JSON.parse(content);
  } catch(error) {
    throw new Error(`Failed to parse JSON content: ${error}`)
  }

  if (extractionRoot && extractionRoot !== '') {
    try {
      fileContent = getNestedJsonContent(fileContent, extractionRoot)
    } catch(error) {
      throw new Error(`Failed to get nested JSON content: ${error}`);
    }
  }

  // Check if fileContent must be converted to array.
  if (!(Symbol.iterator in Object(fileContent))) {
    fileContent = new Array(fileContent);
  }

  return fileContent;
}

/**
 * Parses CSV content into an array of objects using PapaParse.
 *
 * @param content - Raw CSV string content.
 * @param csvDelimiter - The delimiter used in the CSV (e.g., ',' or ';').
 * @returns An array of parsed rows as objects, or null if parsing fails.
 */
export function loadCsvContent(
  content: string,
  csvDelimiter: string,
): any[] | null {
  try {
    const parserResult = Papa.parse<Record<string, any>>(content, {
      header: true,
      delimiter: csvDelimiter,
      skipEmptyLines: true,
      dynamicTyping: false
    });

    if (parserResult.errors.length > 0) {
      throw new Error(`CSV parsing errors: ${parserResult.errors}`)
    }
    return parserResult.data;
  } catch (error) {
    throw new Error(`An error occurred during csv parsing: ${error}`);
  }
}

/**
 * Retrieves a nested value from a JSON-like object using a string path.
 *
 * Supports dot notation (e.g., "user.address.city") and bracket notation
 * (e.g., "user['address']['city']" or "user[0].name") to access deeply nested properties.
 *
 * @param {object} fileContent - The JSON object to extract data from.
 * @param {string} extractionRoot - The path string indicating the nested property to retrieve.
 * @returns {*} - The value at the specified path, or undefined if the path is invalid.
 */
export function getNestedJsonContent< T = any>(
  fileContent: unknown,
  extractionRoot: string
): T | undefined {
  if (typeof fileContent !== 'object' || fileContent == null) return;

  const pathParts = extractionRoot
    .replace(/\[(\w+)]/g, '.$1') // convert brackets to dot notation
    .replace(/^\./, '') // remove leading dot
    .split('.');

  let current: any = fileContent;

  for (const key of pathParts) {
    if (current != null && key in current) {
      current = current[key];
    } else {
      return undefined;
    }
  }

  return current as T;
}

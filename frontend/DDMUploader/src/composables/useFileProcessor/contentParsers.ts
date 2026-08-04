import Papa from "papaparse";
import {ERROR_CATALOG} from "@uploader/utils/errorCatalog";
import {Blueprint} from "@uploader/types/Blueprint";
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";
import {extractData, getFieldKeyMap, getMissingFields} from "@uploader/composables/useFileProcessor/extractionEngine";
import {CSVParserConfig, JSONParserConfig, TXTParserConfig} from "@uploader/types/ParserConfigs";

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
  // Exit early, if no fields to extract are defined.
  if (blueprint.fields_to_extract.length === 0) {
    blueprintOutcomeMap[blueprint.id].registerError(ERROR_CATALOG.NO_FIELDS_TO_EXTRACT, {});
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
    const keyMap = getFieldKeyMap(dataRow, blueprint.extraction_fields, blueprint.id, blueprintOutcomeMap);
    extractData(dataRow, blueprint.fields_to_extract, blueprint.extraction_rules, keyMap, blueprint.id, blueprintOutcomeMap);
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

  switch (blueprint.parser_config.format) {
    case "csv":
      try {
        parsedContentArray = parseCsvContent(content, blueprint.parser_config);
      } catch (error) {
        blueprintOutcomeMap[blueprint.id].registerError(
          ERROR_CATALOG.PARSING_ERROR, {contentType: 'CSV', error: error}
        );
      }
      break;
    case "json":
      try {
        parsedContentArray = parseJsonContent(content, blueprint.parser_config);
      } catch (error) {
        blueprintOutcomeMap[blueprint.id].registerError(
          ERROR_CATALOG.PARSING_ERROR, {contentType: 'JSON', error: error}
        );
      }
      break;
    case "txt":
      try {
        parsedContentArray = parseTxtContent(content, blueprint.parser_config);
      } catch (error) {
        blueprintOutcomeMap[blueprint.id].registerError(
          ERROR_CATALOG.PARSING_ERROR, {contentType: 'TXT', error: error}
        );
      }
      break;
    default:
      blueprintOutcomeMap[blueprint.id].registerError(
        ERROR_CATALOG.UNSUPPORTED_BP_FORMAT, {format: blueprint.parser_config}
      );
      return null;
  }

  if (!parsedContentArray){
    blueprintOutcomeMap[blueprint.id].registerError(
      ERROR_CATALOG.PARSING_ERROR, {contentType: blueprint.parser_config.format}
    );
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
 * @param content - Raw JSON content as a string.
 * @param parserConfig - The parser config.
 * @returns - An array of extracted entries, or null if parsing or extraction fails.
 */
export function parseJsonContent(
  content: string,
  parserConfig: JSONParserConfig,
): ParsedData[] | null {
  let fileContent: any;

  try {
    fileContent = JSON.parse(content);
  } catch(error) {
    throw new Error(`Failed to parse JSON content: ${error}`)
  }

  if (parserConfig.extraction_root && parserConfig.extraction_root !== '') {
    try {
      fileContent = getNestedJsonContent(fileContent, parserConfig.extraction_root)
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
 * @param parserConfig - The CSV parser config.
 * @returns An array of parsed rows as objects.
 */
export function parseCsvContent(
  content: string,
  parserConfig: CSVParserConfig,
): any[] | null {
  try {
    const parserResult = Papa.parse<Record<string, any>>(content, {
      header: true,
      delimiter: parserConfig.delimiter,
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
 * Parses TXT content into an array of objects.
 *
 * @param content - Raw txt string content.
 * @param parserConfig - The txt parser config.
 * @returns An array of parsed rows as objects.
 */
export function parseTxtContent(
  content: string,
  parserConfig: TXTParserConfig,
): ParsedData[] | null {
  const {
    record_separator,
    field_separator,
    kv_separator,
    skip_header_lines,
    skip_footer_lines,
    ignore_blank_lines,
    trim_whitespace,
  } = parserConfig;

  let lines: string[];

  try {
    lines = content.split("\n");
  } catch (error) {
    throw new Error(`Failed to split content into lines: ${error}`);
  }

  // Apply header/footer skipping.
  const start = skip_header_lines ?? 0;
  const end = lines.length - (skip_footer_lines ?? 0);
  lines = lines.slice(start, Math.max(start, end));

  const trimmedContent = lines.join("\n");

  // Split into records.
  let rawRecords: string[];
  try {
    rawRecords = trimmedContent.split(record_separator);
  } catch (error) {
    throw new Error(`Failed to split content into records: ${error}`);
  }

  const records: ParsedData[] = [];

  for (const rawRecord of rawRecords) {
    const record = trim_whitespace ? rawRecord.trim() : rawRecord;

    if (ignore_blank_lines && record === "") {
      continue;
    }

    let fieldLines: string[];
    try {
      fieldLines = record.split(field_separator);
    } catch (error) {
      throw new Error(`Failed to split record into fields: ${error}`);
    }

    const parsedRecord: ParsedData = {};

    for (let fieldLine of fieldLines) {
      if (trim_whitespace) {
        fieldLine = fieldLine.trim();
      }

      if (ignore_blank_lines && fieldLine === "") {
        continue;
      }

      const separatorIndex = fieldLine.indexOf(kv_separator);

      if (separatorIndex === -1) {
        // No kv separator found on this line; skip it (field-level
        // matching/labeling is handled downstream).
        continue;
      }

      let key = fieldLine.slice(0, separatorIndex);
      let value: string | string[] = fieldLine.slice(
        separatorIndex + kv_separator.length,
      );

      if (trim_whitespace) {
        key = key.trim();
        value = (value as string).trim();
      }

      // Collect repeated keys into an array rather than overwriting.
      if (key in parsedRecord) {
        parsedRecord[key] = `${parsedRecord[key]}, ${value}`;
      } else {
        parsedRecord[key] = value;
      }
    }

    records.push(parsedRecord);
  }

  return records;
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

import {
  regexDeleteMatch, regexDeleteRow, regexReplaceMatch,
  valueIsEqual, valueIsGreater,
  valueIsGreaterOrEqual,
  valueIsNotEqual, valueIsSmaller,
  valueIsSmallerOrEqual
} from "@uploader/utils/ExtractionFunctions";
import {ERROR_CATALOG} from "@uploader/utils/errorCatalog";
import {ExtractionRule} from "@uploader/types/ExtractionRule";
import {ExtractionField} from "@uploader/types/ExtractionField";
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";

/**
 * Determines which expected fields are missing from a data row.
 *
 * Supports both exact key matching and regex-based matching.
 *
 * @param dataRow - An object representing the row of data (key-value pairs).
 * @param expectedFields - A list of field names or patterns to expect.
 * @param regexMatching - If true, treats expected fields as regular expressions for key matching.
 * @returns An array of expected fields that are not found in the data row.
 */
export function getMissingFields(
  dataRow: Record<string, any>,
  expectedFields: string[],
  regexMatching: boolean
): string[] {
  let missingFields: string[] = [];

  for (const field of expectedFields) {
    const matchFound = regexMatching
      ? Object.keys(dataRow).some(key => new RegExp(field).test(key))
      : Object.prototype.hasOwnProperty.call(dataRow, field);

    if (!matchFound) {
      missingFields.push(field);
    }
  }
  return missingFields;
}

/**
 * Builds a mapping between expected fields and actual keys in the data row.
 *
 * Attempts to match each extraction field against the keys in the data row,
 * using either exact string matching or a regular expression,
 * depending on the `match_regex` flag.
 *
 * If multiple keys match a field, the first is used and a warning is recorded.
 * If no match is found, an error is recorded.
 * All errors and warnings are pushed to the `extractionOutcome.extractionErrors` array.
 *
 * @param dataRow - The object representing a row of data with string keys.
 * @param extractionFields - Array of extraction rule objects.
 * @param blueprintId - The numerical ID of the currently processed blueprint.
 * @param blueprintOutcomeMap - A map of blueprint ids to their extraction outcome.
 * @returns A Map where each key is the extraction field name and the value is
 *   the corresponding matched key in the dataRow.
 */
export function getFieldKeyMap(
  dataRow: Record<string, any>,
  extractionFields: ExtractionField[],
  blueprintId: number,
  blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>
): Map<string, string> {
  const fieldKeyMap = new Map<string, string>();

  for (const field of extractionFields) {
    const field_name = field.alias ? field.alias : field.expected_name

    if (fieldKeyMap.has(field_name)) {
      continue;
    }

    const keys = (() => {
      if (field.match_regex) {
        let pattern: RegExp;
        try {
          pattern = new RegExp(field.expected_name);
        } catch (error) {
          blueprintOutcomeMap[blueprintId].registerError(
            ERROR_CATALOG.INVALID_FIELD_REGEX, {blueprintId: blueprintId, fieldExpectedName: field.expected_name}
          );
          return [];
        }
        return Object.keys(dataRow).filter(key => pattern.test(key));
      }
      return Object.keys(dataRow).filter(key => field.expected_name === key);
    })();

    if(keys.length > 1) {
      const errorContext = { field: field.expected_name, keys: keys, defaultKey: keys[0] };
      blueprintOutcomeMap[blueprintId].registerError(ERROR_CATALOG.MORE_THAN_ONE_KEY_MATCH, errorContext);
      fieldKeyMap.set(field_name, keys[0]);
      blueprintOutcomeMap[blueprintId].mapExtractedKey(field_name, keys[0]);
    } else if(keys.length === 0) {
      blueprintOutcomeMap[blueprintId].registerNoKeyMatch(field.expected_name, Object.keys(dataRow));
    } else {
      fieldKeyMap.set(field_name, keys[0]);
      blueprintOutcomeMap[blueprintId].mapExtractedKey(field_name, keys[0]);
    }

  }
  return fieldKeyMap;
}

/**
 * Applies a set of extraction rules to a data row and stores the extracted data.
 *
 * This function:
 * 1. Creates an object to hold extracted field values
 * 2. Processes each rule against the data row
 * 3. Applies comparison operators that may filter out rows
 * 4. Applies transformation operators that modify field values
 * 5. Adds the extracted data to the blueprint's outcome
 *
 * Comparison operators (==, !=, >, <, etc.) can cause the entire row to be discarded.
 * Transformation operators (regex-delete-match, etc.) modify field values in place.
 *
 * @param dataRow - A single row of data as a key-value object
 * @param fieldsToExtract - List of the fields to keep in extracted data
 * @param extractionRules - Array of rules defining how to process fields
 * @param fieldKeyMap - Mapping from rule field names to actual data keys
 * @param blueprintId - ID of the blueprint being processed
 * @param blueprintOutcomeMap - Map of blueprint outcomes
 */
export function extractData(
  dataRow: Record<string, any>,
  fieldsToExtract: string[],
  extractionRules: ExtractionRule[],
  fieldKeyMap: Map<string, string>,
  blueprintId: number,
  blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>
): void | null {
  const extractedRowData: Record<string, any> = {};

  for (const rule of extractionRules) {
    const key = fieldKeyMap.get(rule.field);

    if (key === undefined) {
      // TODO: Log undefined key
      continue;
    }

    switch (rule.comparison_operator) {
      case null:
        // Note: Deprecated; should not be triggered.
        break;

      case '':
        // Note: Deprecated; should not be triggered.
        break;

      case '==':
        if (valueIsEqual(dataRow[key], rule.comparison_value)) return discardRow(rule, blueprintId, blueprintOutcomeMap);
        break;

      case '!=':
        if (valueIsNotEqual(dataRow[key], rule.comparison_value)) return discardRow(rule, blueprintId, blueprintOutcomeMap);
        break;

      case '<=':
        if (valueIsSmallerOrEqual(dataRow[key], rule.comparison_value)) return discardRow(rule, blueprintId, blueprintOutcomeMap);
        break;

      case '>=':
        if (valueIsGreaterOrEqual(dataRow[key], rule.comparison_value)) return discardRow(rule, blueprintId, blueprintOutcomeMap);
        break;

      case '<':
        if (valueIsSmaller(dataRow[key], rule.comparison_value)) return discardRow(rule, blueprintId, blueprintOutcomeMap);
        break;

      case '>':
        if (valueIsGreater(dataRow[key], rule.comparison_value)) return discardRow(rule, blueprintId, blueprintOutcomeMap);
        break;

      case 'regex-delete-match':
        if (key in dataRow) {
          try {
            dataRow[key] = regexDeleteMatch(dataRow[key], rule.comparison_value);
            blueprintOutcomeMap[blueprintId].extractionRuleLog[rule.id] += 1;
          } catch {
            break;
          }
        }
        break;

      case 'regex-replace-match':
        if (key in dataRow) {
          try {
            dataRow[key] = regexReplaceMatch(dataRow[key], rule.comparison_value, rule.replacement_value);
            blueprintOutcomeMap[blueprintId].extractionRuleLog[rule.id] += 1;
          } catch {
            break;
          }
        }
        break;

      case 'regex-delete-row':
        if (key in dataRow) {
          let deleteRow = false;
          try {
            deleteRow = regexDeleteRow(dataRow[key], rule.comparison_value);
          } catch {
            break;
          }
          if (deleteRow) {
            return discardRow(rule, blueprintId, blueprintOutcomeMap);
          }
        }
        break;
      default: break;
    }
  }
  if (Object.keys(dataRow).length > 0) {
    for (const [field, key] of fieldKeyMap.entries()) {
      if (key in dataRow && fieldsToExtract.includes(field)) {
        extractedRowData[field] = dataRow[key];
      }
    }
    if (Object.keys(extractedRowData).length > 0) {
      blueprintOutcomeMap[blueprintId].extractedData.push(extractedRowData);
    } else {
      // TODO: Log no keys extracted
    }
  }
  return;
}

/**
 * Marks a row as discarded due to a filtering rule and updates extraction statistics.
 *
 * @param rule - The extraction rule that triggered the discard
 * @param blueprintId - ID of the blueprint being processed
 * @param blueprintOutcomeMap - Map of blueprint outcomes
 * @returns null to signal row discard
 */
export function discardRow(
  rule: ExtractionRule,
  blueprintId: number,
  blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>
): null {
  blueprintOutcomeMap[blueprintId].incrementExtractionRuleCount(rule);
  return;
}

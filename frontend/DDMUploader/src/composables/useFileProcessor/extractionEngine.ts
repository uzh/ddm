import {
  regexDeleteMatch, regexDeleteRow, regexReplaceMatch,
  valueIsEqual, valueIsGreater,
  valueIsGreaterOrEqual,
  valueIsNotEqual, valueIsSmaller,
  valueIsSmallerOrEqual
} from "@uploader/utils/ExtractionFunctions";
import {ERROR_CATALOG} from "@uploader/utils/errorCatalog";
import {ExtractionRule} from "@uploader/types/ExtractionRule";
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
 * Builds a mapping between expected fields (defined in extraction rules) and actual keys in the data row.
 *
 * For each rule, the function attempts to match the rule's field against the keys in the data row,
 * using either exact string matching or a regular expression, depending on the `regex_field` flag.
 *
 * If multiple keys match a rule, the first is used and a warning is recorded.
 * If no match is found, an error is recorded.
 * All errors and warnings are pushed to the `extractionOutcome.extractionErrors` array.
 *
 * @param dataRow - The object representing a row of data with string keys.
 * @param extractionRules - Array of extraction rule objects.
 * @param blueprintId - The numerical ID of the currently processed blueprint.
 * @param blueprintOutcomeMap - A map of blueprint ids to their extraction outcome.
 * @returns A Map where each key is the rule field name and the value is the corresponding key in the dataRow.
 */
export function getKeyMap(
  dataRow: Record<string, any>,
  extractionRules: ExtractionRule[],
  blueprintId: number,
  blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>
): Map<string, string> {
  const keyMap = new Map<string, string>;

  for (const rule of extractionRules) {
    const keys = Object.keys(dataRow).filter(key => {
      if (rule.regex_field) {
        try {
          return new RegExp(rule.field).test(key);
        } catch (error) {
          blueprintOutcomeMap[blueprintId].registerError(
            ERROR_CATALOG.INVALID_REGEX, {blueprintId: blueprintId, ruleId: rule.id, ruleRegex: rule.field}
          );
          return false;
        }
      }
      return rule.field === key
    });

    if(keys.length > 1) {
      const errorContext = { field: rule.field, keys: keys, defaultKey: keys[0] };
      blueprintOutcomeMap[blueprintId].registerError(ERROR_CATALOG.MORE_THAN_ONE_KEY_MATCH, errorContext);
      keyMap.set(rule.field, keys[0]);
      blueprintOutcomeMap[blueprintId].mapExtractedField(rule.field, keys[0]);
    } else if(keys.length === 0) {
      blueprintOutcomeMap[blueprintId].registerNoKeyMatch(rule.field, Object.keys(dataRow));
    } else {
      keyMap.set(rule.field, keys[0]);
      blueprintOutcomeMap[blueprintId].mapExtractedField(rule.field, keys[0]);
    }
  }
  return keyMap;
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
 * @param extractionRules - Array of rules defining how to process fields
 * @param keyMap - Mapping from rule field names to actual data keys
 * @param blueprintId - ID of the blueprint being processed
 * @param blueprintOutcomeMap - Map of blueprint outcomes
 */
export function extractData(
  dataRow: Record<string, any>,
  extractionRules: ExtractionRule[],
  keyMap: Map<string, string>,
  blueprintId: number,
  blueprintOutcomeMap: Record<number, BlueprintExtractionOutcome>
): void | null {
  const extractedRowData: Record<string, any> = {};

  for (const rule of extractionRules) {
    const key = keyMap.get(rule.field);

    if (key === undefined) {
      break;
    }

    switch (rule.comparison_operator) {
      case null:
        extractedRowData[rule.field] = dataRow[key];
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
        if (key in extractedRowData) {
          try {
            let newValue = regexDeleteMatch(dataRow[key], rule.comparison_value);
            extractedRowData[rule.field] = newValue;
            dataRow[key] = newValue;
            blueprintOutcomeMap[blueprintId].extractionRuleLog[rule.id] += 1;
          } catch {
            // Fallback if an error occurs.
            extractedRowData[rule.field] = dataRow[key];
          }
        }
        break;

      case 'regex-replace-match':
        if (key in extractedRowData) {
          try {
            let newValue = regexReplaceMatch(dataRow[key], rule.comparison_value, rule.replacement_value);
            extractedRowData[rule.field] = newValue;
            dataRow[key] = newValue;
            blueprintOutcomeMap[blueprintId].extractionRuleLog[rule.id] += 1;
          } catch {
            // Fallback if an error occurs.
            extractedRowData[rule.field] = dataRow[key];
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

  if (Object.keys(extractedRowData).length > 0) {
    blueprintOutcomeMap[blueprintId].extractedData.push(extractedRowData);
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

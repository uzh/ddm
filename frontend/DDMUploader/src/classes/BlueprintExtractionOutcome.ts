import {ProcessingError} from "@uploader/types/ProcessingError";
import {Blueprint} from "@uploader/types/Blueprint";
import {ExtractionRule} from "@uploader/types/ExtractionRule";

/**
 * Class: BlueprintExtractionOutcome
 *
 * Represents the outcome of processing a blueprint within the uploader system.
 * Tracks extracted data, stats, rule usage logs, field mappings, and any
 * processing errors encountered.
 *
 * Constructor:
 *  - Accepts a Blueprint object and initializes internal tracking structures.
 *
 * Main Features:
 *  - Logs rule application stats.
 *  - Maps extracted fields to rule-defined fields.
 *  - Collects detailed error records with contextual information.
 *  - Tracks unmatchable fields for audit/debugging.
 *
 * Fields:
 *  - blueprintId: ID of the blueprint being processed.
 *  - extractedData: Array of rows or objects extracted from input.
 *  - extractedFieldsMap: Maps field names to the extraction rule field they came from.
 *  - extractionStats: Summary of rows with missing fields, (filtered) row counts and unmatched keys.
 *  - extractionRuleLog: Records how many times each extraction rule was triggered.
 *  - processingErrors: Collected error metadata for review and logging.
 */
export class BlueprintExtractionOutcome {
  blueprintId: number;
  extractedData: any[];  // eslint-disable-line @typescript-eslint/no-explicit-any
    // Usually, this is an array of dictionaries, with each dictionary holding extracted-field:value pairs.
  rowGroupIds: number[];
    // Parallel array to extractedData: rowGroupIds[i] is the id of the root
    // item that produced extractedData[i]. Rows sharing a group id came
    // from the same root item (e.g. the same conversation). This is
    // purely a display/UI concern -- it is never part of extractedData
    // itself, and therefore never sent as part of the donated data.
    // Populated for every row, not just nested-loop rows.
  extractedFieldsMap: Map<string, string>;  // Used to map the name of extracted fields to the field definition used in extraction rules.
  extractionStats: {
    nRowsMissingField: number,
    nRowsFilteredOut: number,
    nRowsTotal: number,
    noKeyMatches: Record<string, Record<string, number>>  // Maps the expected field to a record in which the key is a stringified array of available fields and the value is the count of how many times this was encountered.
    nNestedRowsTotal: number,  // Total number of nested-loop items encountered across all root items (0 if the blueprint has no nested_loop_path configured).
    nNestedRowsMissingField: number,  // Number of nested-loop items skipped due to failing the nested_expected_fields check.
  };
  extractionRuleLog: Record<string, number>;  // Record where the key is the rule.id and the value represents how many times the rule was triggered.
  processingErrors: ProcessingError[];
  excludedGroupIds: Set<number>;
    // Group ids (see rowGroupIds) the participant has chosen to exclude
    // from their donation, via the "remove this entry" control (only
    // available when the blueprint.nested_entry_exclusion_allowed
    // is set). Non-destructive/reversible: extractedData/rowGroupIds are
    // never mutated here, so toggling exclusion is trivial and the actual
    // filtering only happens once, at submission time (see useDataSubmitter).
  private groupIdCounter: number;

  constructor(blueprint: Blueprint) {
    this.blueprintId = blueprint.id
    this.extractedData = []
    this.rowGroupIds = []
    this.groupIdCounter = 0
    this.excludedGroupIds = new Set()
    this.extractedFieldsMap = new Map()
    this.extractionStats = {
      nRowsMissingField: 0,
      nRowsFilteredOut: 0,
      nRowsTotal: 0,
      noKeyMatches: {},
      nNestedRowsTotal: 0,
      nNestedRowsMissingField: 0,
    }
    this.extractionRuleLog = this.initializeExtractionRuleLog(blueprint.extraction_rules)
    this.processingErrors = []
  }

  initializeExtractionRuleLog(extractionRules: ExtractionRule[]): Record<string, number> {
    return Object.fromEntries(extractionRules.map(rule => [rule.id, 0]));
  }

  /**
   * Returns a new, unique group id, identifying one root item across
   * however many rows it ends up producing (zero or more). Call once per
   * root item, regardless of how many rows (if any) it contributes to
   * extractedData.
   */
  nextGroupId(): number {
    return this.groupIdCounter++;
  }

  /**
   * Toggles whether a group (root item) is excluded from the donation.
   * Reversible -- calling this again on the same group id restores it.
   */
  toggleGroupExclusion(groupId: number): void {
    if (this.excludedGroupIds.has(groupId)) {
      this.excludedGroupIds.delete(groupId);
    } else {
      this.excludedGroupIds.add(groupId);
    }
  }

  /**
   * Increments statistics for a row that was filtered out during extraction.
   *
   * When rows don't meet extraction criteria, this method updates the relevant counters
   * and logs which extraction rule triggered the filtering.
   *
   * @param extractionRule - The rule that determined the row should be discarded
   */
  incrementExtractionRuleCount(extractionRule: ExtractionRule) {
    this.extractionStats.nRowsFilteredOut += 1;
    this.extractionRuleLog[extractionRule.id] += 1;
  }

  /**
   * Records instances where expected fields couldn't be matched with available fields for debugging and analysis purposes.
   *
   * @param expectedField - The field name that was expected but not found
   * @param availableFields - List of fields that were available for matching
   */
  registerNoKeyMatch(expectedField: string, availableFields: string[]): void {
    if (!this.extractionStats.noKeyMatches[expectedField]) {
      this.extractionStats.noKeyMatches[expectedField] = {};
    }

    const lookupKey = JSON.stringify([...availableFields].sort());  // e.g., "['availableFieldA', 'availableFieldB']"
    if (!this.extractionStats.noKeyMatches[expectedField][lookupKey]) {
      this.extractionStats.noKeyMatches[expectedField][lookupKey] = 0;
    }
    this.extractionStats.noKeyMatches[expectedField][lookupKey] += 1;
  }

  /**
   * Adds an occurred error to the processingErrors array.
   *
   * @param error - the ProcessingError that occurred.
   * @param context - a dictionary holding context information used to render the error description (see errorCatalog
   *                  for details on the expected context for each error).
   */
  registerError(error: ProcessingError, context: Record<string, unknown>): void {
    this.processingErrors.push({
      type: error.type,
      category: error.category,
      scope: error.scope,
      i18nDetail: error.i18nDetail,
      level: error.level,
      context: { ...error.context, ...context, blueprintId: this.blueprintId }
    } as ProcessingError)
  }

  /**
   * Associates an extracted key with its corresponding extraction field.
   *
   * Maintains a mapping between field names (key) found in the data and their formal definitions
   * in extraction fields. The first mapping for each field is preserved.
   *
   * @param expectedField - The formal field name from the extraction field
   * @param extractedKey - The field name as found in the extracted data
   */
  mapExtractedKey(expectedField: string, extractedKey: string): void {
    if (!this.extractedFieldsMap.has(expectedField)) {
      this.extractedFieldsMap.set(expectedField, extractedKey);
    }
  }
}

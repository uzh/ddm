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
 *  - extractionLog: Records how many times each extraction rule was triggered.
 *  - processingErrors: Collected error metadata for review and logging.
 */
export class BlueprintExtractionOutcome {
  blueprintId: number;
  extractedData: any[];  // Usually, this is an array of dictionaries, with each dictionary holding extracted-field:value pairs.
  extractedFieldsMap: Map<string, string>;  // Used to map the name of extracted fields to the field definition used in extraction rules.
  extractionStats: {
    nRowsMissingField: number,
    nRowsFilteredOut: number,
    nRowsTotal: number,
    noKeyMatches: Record<string, Record<string, number>>  // Maps the expected field to a record in which the key is a stringified array of available fields and the value is the count of how many times this was encountered.
  };
  extractionRuleLog: Record<string, number>;  // Record where the key is the rule.id and the value represents how many times the rule was triggered.
  processingErrors: ProcessingError[];

  constructor(blueprint: Blueprint) {
    this.blueprintId = blueprint.id
    this.extractedData = []
    this.extractedFieldsMap = new Map()
    this.extractionStats = {
      nRowsMissingField: 0,
      nRowsFilteredOut: 0,
      nRowsTotal: 0,
      noKeyMatches: {}
    }
    this.extractionRuleLog = this.initializeExtractionRuleLog(blueprint.extraction_rules)
    this.processingErrors = []
  }

  initializeExtractionRuleLog(extractionRules: ExtractionRule[]): Record<string, number> {
    return Object.fromEntries(extractionRules.map(rule => [rule.id, 0]));
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
   * Associates an extracted field name with its corresponding rule-defined field.
   *
   * Maintains a mapping between field names found in the data and their formal definitions
   * in extraction rules. The first mapping for each field is preserved.
   *
   * @param extractedField - The field name as found in the extracted data
   * @param ruleField - The formal field name from the extraction rule
   */
  mapExtractedField(extractedField: string, ruleField: string): void {
    if (!this.extractedFieldsMap.has(extractedField)) {
      this.extractedFieldsMap.set(extractedField, ruleField);
    }
  }
}

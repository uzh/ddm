/**
 * Centralized collection of extraction states that can be used for overall extraction state description and
 * blueprint state description.
 */
export const EXTRACTION_STATES = {
  DATA_EXTRACTED: 'DATA_EXTRACTED',        // (Every) blueprint has been extracted without encountering any errors.
  PARTIAL: 'PARTIAL',                      // Some blueprints have been successfully extracted, others have encountered errors (only on file-level).
  FAILED: 'FAILED',                        // No data has been extracted due to (a) critical error(s).
  NOT_ATTEMPTED: 'NOT_ATTEMPTED',          // Extraction not yet attempted.
  NO_DATA_EXTRACTED: 'NO_DATA_EXTRACTED'   // No data has been extracted but no errors occurred (usually means that all entries have been filtered out).
} as const;

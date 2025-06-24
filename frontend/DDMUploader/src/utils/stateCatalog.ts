/**
 * Centralized collection of extraction states that can be used for overall extraction state description and
 * blueprint state description.
 */
export const EXTRACTION_STATES = {
  SUCCESS: 'success',           // (Every) blueprint has been extracted without encountering any errors.
  PARTIAL: 'partial',           // Some blueprints have been successfully extracted, others have encountered errors (only on file-level).
  FAILED: 'failed',             // No data has been extracted due to (a) critical error(s).
  PENDING: 'pending',           // Extraction not yet attempted.
  NO_DATA: 'no data extracted'  // No data has been extracted but no errors occurred (usually means that all entries have been filtered out).
} as const;

import {ERROR_CATEGORIES, ERROR_LEVELS, ERROR_SCOPES, ProcessingError} from "@uploader/types/ProcessingError";

/**
 * Error Catalog
 *
 * A centralized collection of error definitions for the uploader system.
 * These standardized error objects provide consistent error reporting
 * with proper categorization, severity levels, and i18n support.
 */
export const ERROR_CATALOG: Record<string, ProcessingError> = {
  INVALID_ZIP: {
    type: 'INVALID_ZIP',
    category: ERROR_CATEGORIES.ZIP_HANDLING,
    scope: ERROR_SCOPES.FILE,
    i18nDetail: 'errors.invalid-zip',
    level: ERROR_LEVELS.CRITICAL,
    context: {
      fileType: '[invalid file type]'
    }
  },
  ZIP_READ_FAIL: {
    type: 'ZIP_READ_FAIL',
    category: ERROR_CATEGORIES.ZIP_HANDLING,
    scope: ERROR_SCOPES.FILE,
    i18nDetail: 'errors.zip-read-fail',
    level: ERROR_LEVELS.CRITICAL,
    context: {}
  },
  INVALID_REGEX: {
    type: 'INVALID_REGEX',
    category: ERROR_CATEGORIES.BLUEPRINT_SPECIFICATION,
    scope: ERROR_SCOPES.BLUEPRINT,
    i18nDetail: 'errors.invalid-regex',
    level: ERROR_LEVELS.CRITICAL,
    context: {
      blueprintId: '[blueprint ID]',
    }
  },
  INVALID_RULE_REGEX: {
    type: 'INVALID_RULE_REGEX',
    category: ERROR_CATEGORIES.EXTRACTION,
    scope: ERROR_SCOPES.BLUEPRINT,
    i18nDetail: 'errors.invalid-rule-regex',
    level: ERROR_LEVELS.WARN,
    context: {
      blueprintId: '[blueprint ID]',
      ruleId: '[rule ID]',
      ruleRegex: '[rule regex]'
    }
  },
  NO_FILE_MATCH: {
    type: 'NO_FILE_MATCH',
    category: ERROR_CATEGORIES.EXTRACTION,
    scope: ERROR_SCOPES.BLUEPRINT,
    i18nDetail: 'errors.no-file-match',
    level: ERROR_LEVELS.CRITICAL,
    context: {
      blueprintId: '[blueprint ID]',
      regexPath: '[provided regex path]',
      availableFiles: '[list of files in zip]'
    }
  },
  FILE_PROCESSING_FAIL_GENERAL: {
    type: 'FILE_PROCESSING_FAIL_GENERAL',
    category: ERROR_CATEGORIES.FILE_PROCESSING,
    scope: ERROR_SCOPES.BLUEPRINT,
    i18nDetail: 'errors.file-processing-fail-general',
    level: ERROR_LEVELS.CRITICAL,
    context: {
      blueprintId: '[blueprint ID]',
      error: '[the error that occurred]'
    }
  },
  STRING_CONVERSION_ERROR: {
    type: 'STRING_CONVERSION_ERROR',
    category: ERROR_CATEGORIES.FILE_PROCESSING,
    scope: ERROR_SCOPES.FILE,
    i18nDetail: 'errors.string-conversion-error',
    level: ERROR_LEVELS.CRITICAL,
    context: {}
  },
  NO_EXTRACTION_RULES: {
    type: 'NO_EXTRACTION_RULES',
    category: ERROR_CATEGORIES.BLUEPRINT_SPECIFICATION,
    scope: ERROR_SCOPES.BLUEPRINT,
    i18nDetail: 'errors.no-extraction-rules',
    level: ERROR_LEVELS.CRITICAL,
    context: {
      blueprintId: '[blueprint ID]',
    }
  },
  PARSING_ERROR: {
    type: 'PARSING_ERROR',
    category: ERROR_CATEGORIES.FILE_PROCESSING,
    scope: ERROR_SCOPES.BLUEPRINT,
    i18nDetail: 'errors.parsing-error',
    level: ERROR_LEVELS.CRITICAL,
    context: {
      blueprintId: '[blueprint ID]',
      contentType: '[the type of content it tried to parse]'
    }  // optional: error
  },
  UNSUPPORTED_BP_FORMAT: {
    type: 'UNSUPPORTED_BP_FORMAT',
    category: ERROR_CATEGORIES.BLUEPRINT_SPECIFICATION,
    scope: ERROR_SCOPES.BLUEPRINT,
    i18nDetail: 'errors.unsupported-bp-format',
    level: ERROR_LEVELS.CRITICAL,
    context: {
      blueprintId: '[blueprint ID]',
      format: '[name of unsupported format]'
    }
  },
  MORE_THAN_ONE_KEY_MATCH: {
    type: 'MORE_THAN_ONE_KEY_MATCH',
    category: ERROR_CATEGORIES.EXTRACTION,
    scope: ERROR_SCOPES.BLUEPRINT,
    i18nDetail: 'errors.more-than-one-key-match',
    level: ERROR_LEVELS.INFO,
    context: {
      blueprintId: '[blueprint ID]',
      field: '[the field for which multiple matches were found]',
      keys: '[the keys that were matched]',
      defaultKey: '[the fallback key used]'
    }
  },
}

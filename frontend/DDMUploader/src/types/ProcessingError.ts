export const ERROR_LEVELS = {
  INFO: 'info',
  WARN: 'warn',
  CRITICAL: 'critical',
}

export type ErrorLevel = typeof ERROR_LEVELS[keyof typeof ERROR_LEVELS];

export const ERROR_SCOPES = {
  FILE: 'file',
  BLUEPRINT: 'blueprint',
}

export type ErrorScope = typeof ERROR_SCOPES[keyof typeof ERROR_SCOPES];

export const ERROR_CATEGORIES = {
  ZIP_HANDLING: 'ZIP handling error',
  FILE_PROCESSING: 'File processing error',
  BLUEPRINT_SPECIFICATION: 'Blueprint specification error',
  EXTRACTION: 'Extraction error'
}

export type ErrorCategory = typeof ERROR_CATEGORIES[keyof typeof ERROR_CATEGORIES];

export type ProcessingError = {
  type: string,
  category: ErrorCategory;
  scope: ErrorScope;
  i18nDetail: string;
  level: ErrorLevel;
  context: Record<string, any>;  // If scope is == 'blueprint', blueprintId must be saved in context.
}

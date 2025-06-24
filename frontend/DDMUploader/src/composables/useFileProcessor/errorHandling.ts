import {ProcessingError} from "@uploader/types/ProcessingError";

/**
 * Registers a general error in the provided errors collection.
 *
 * This function takes an error from the error catalog and enhances it with
 * additional context information, then adds it to the specified errors collection.
 * The original error's properties are preserved, with additional context merged in.
 *
 * @param errorsCollection - The array where the error should be registered
 * @param catalogError - The base error definition from the error catalog
 * @param context - Additional contextual information about this specific error instance
 *
 * @example
 * ```typescript
 * // Register a file parsing error with additional context
 * registerGeneralError(
 *   errors,
 *   ERROR_CATALOG.PARSING_ERROR,
 *   { fileName: "data.csv", lineNumber: 42 }
 * );
 * ```
 */
export function registerGeneralError(
  errorsCollection: ProcessingError[],
  catalogError: ProcessingError,
  context: Record<string, any> = {}
): void {
  const error: ProcessingError = {
    type: catalogError.type,
    category: catalogError.category,
    scope: catalogError.scope,
    i18nDetail: catalogError.i18nDetail,
    level: catalogError.level,
    context: { ...catalogError.context, ...context }
  }

  errorsCollection.push(error);
}

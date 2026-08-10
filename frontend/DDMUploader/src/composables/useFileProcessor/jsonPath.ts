/**
 * Shared JSON path-resolution helpers, used both by the content parsers
 * (to resolve a blueprint's extraction_root/nested_loop_path) and by the
 * extraction engine (to resolve dot/bracket-path ExtractionField names
 * against a row). Kept in their own module so the two don't import from
 * each other.
 */

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

/**
 * Resolves the nested-loop collection for one root-level item.
 *
 * - Array node -> returned as-is (each element is a nested row).
 * - Plain object node -> Object.values() (keys discarded), so that
 *   ID-keyed objects (e.g. a ChatGPT export's `mapping`) can be looped
 *   over like a list.
 * - Anything else (undefined, null, primitive) -> [] (no nested rows for
 *   this root item).
 *
 * @param rootItem - A single root-level parsed item.
 * @param nestedLoopPath - Path (relative to rootItem) to the nested collection.
 * @returns An array of nested items to process, or [] if none were found.
 */
export function resolveNestedCollection(rootItem: unknown, nestedLoopPath: string): any[] {
  if (!nestedLoopPath) return [];

  const node = getNestedJsonContent(rootItem, nestedLoopPath);

  if (Array.isArray(node)) {
    return node;
  }
  if (node !== null && node !== undefined && typeof node === "object") {
    return Object.values(node);
  }
  return [];
}

function isPrimitive(value: unknown): boolean {
  return value === null || ["string", "number", "boolean"].includes(typeof value);
}

/**
 * Joins an array of primitive values (e.g. strings) into a single string,
 * using the given separator. Non-array values, and arrays containing
 * non-primitive elements (objects/arrays), are returned unchanged.
 *
 * @param value - The resolved field value.
 * @param separator - The separator to join primitive array elements with.
 * @returns The joined string, or the original value if it doesn't apply.
 */
export function joinIfPrimitiveArray(value: unknown, separator: string): unknown {
  if (Array.isArray(value) && value.length > 0 && value.every(isPrimitive)) {
    return value.map(v => (v === null ? "" : String(v))).join(separator);
  }
  return value;
}

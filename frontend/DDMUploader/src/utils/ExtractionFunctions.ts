import { DateTime } from "luxon";


/**
 * Converts any value to its string representation.
 *
 * For string values, returns the original string.
 * For non-string values, converts to JSON string representation.
 *
 * @param v - The value to convert to a string
 * @returns String representation of the value
 */
export function getOriginalValueAsString(v: any): string {
  if (typeof v !== 'string') {
    return JSON.stringify(v);
  } else {
    return v;
  }
}

/**
 * Checks if a value can be interpreted as a number.
 *
 * @param v - The value to check
 * @returns True if the value is a number or can be parsed as a number
 */
export function isNumeric(v: any): boolean {
  if (typeof v === 'number') return true;
  if (typeof v != 'string') return false;
  return !isNaN(parseFloat(v)) && isFinite(Number(v));
}

/**
 * Determines if both values can be parsed as valid dates.
 *
 * Checks multiple date formats:
 * - ISO format (e.g., "2016-05-25T09:24:15.123", "2016-05-25")
 * - RFC2822 format (e.g., "Tue, 01 Nov 2016 13:23:12 +0630")
 * - HTTP format (e.g., "Sunday, 06-Nov-94 08:49:37 GMT")
 *
 * @param entryValue - First value to check
 * @param comparisonValue - Second value to check
 * @returns True if both values can be parsed as dates in the same format
 */
export function bothDates(entryValue: any, comparisonValue: any): boolean {
  try {
    // Try parsing as ISO date format (e.g., "2016-05-25T092415.123", "2016-05-25").
    if (DateTime.fromISO(entryValue).isValid && DateTime.fromISO(comparisonValue).isValid) {
      return true;
    }

    // Try parsing as RFC2822 date format (e.g., "Tue, 01 Nov 2016 13:23:12 +0630").
    if (DateTime.fromRFC2822(entryValue).isValid && DateTime.fromRFC2822(comparisonValue).isValid) {
      return true;
    }

    // Try parsing as HTTP date format (e.g., "Sunday, 06-Nov-94 08:49:37 GMT").
    if (DateTime.fromHTTP(entryValue).isValid && DateTime.fromHTTP(comparisonValue).isValid) {
      return true;
    }

    return false;
  }
  catch(error) {
    console.warn("[bothDates] Error checking date formats:", error);
    return false;
  }
}

/**
 * Parses two values as dates, returning DateTime objects.
 *
 * Attempts to parse using multiple date formats, returning null values
 * if the inputs cannot be parsed as dates.
 *
 * @param entryValue - First value to parse
 * @param comparisonValue - Second value to parse
 * @returns Array containing the two parsed DateTime objects, or null if parsing fails
 */
export function getDates(entryValue: any, comparisonValue: any): [DateTime | null, DateTime | null] {
  try {
    if (DateTime.fromISO(entryValue).isValid && DateTime.fromISO(comparisonValue).isValid) {
      return [DateTime.fromISO(entryValue), DateTime.fromISO(comparisonValue)];
    }

    if (DateTime.fromRFC2822(entryValue).isValid && DateTime.fromRFC2822(comparisonValue).isValid) {
      return [DateTime.fromRFC2822(entryValue), DateTime.fromRFC2822(comparisonValue)];
    }

    if (DateTime.fromHTTP(entryValue).isValid && DateTime.fromHTTP(comparisonValue).isValid) {
      return [DateTime.fromHTTP(entryValue), DateTime.fromHTTP(comparisonValue)];
    }
  } catch (error) {
    console.warn(`[getDates] Error parsing dates: ${error}`);
  }
  return [null, null];
}

/**
 * Prepares two values for comparison by converting them to compatible types.
 *
 * - If both values are dates, converts them to DateTime objects
 * - If both values are numeric, converts them to numbers
 * - Otherwise, converts both to strings
 *
 * @param entryValue - First value to prepare
 * @param comparisonValue - Second value to prepare
 * @returns Array containing the two prepared values
 */
export function prepareValues(entryValue: any, comparisonValue: any): [any, any] {
  if (bothDates(entryValue, comparisonValue)) {
    const [dateEntry, dateComparison] = getDates(entryValue, comparisonValue);
    return [dateEntry, dateComparison];
  } else if (isNumeric(entryValue) && isNumeric(comparisonValue)) {
    return [parseFloat(entryValue), parseFloat(comparisonValue)];
  } else {
    entryValue = getOriginalValueAsString(entryValue);
    comparisonValue = getOriginalValueAsString(comparisonValue);
  }
  return [entryValue, comparisonValue];
}

/**
 * Checks if two values are equal after conversion to strings.
 *
 * @param entryValue - First value to compare
 * @param comparisonValue - Second value to compare
 * @returns True if the string representations are equal
 */
export function valueIsEqual(entryValue: any, comparisonValue: any): boolean {
  try {
    entryValue = getOriginalValueAsString(entryValue);
    comparisonValue = getOriginalValueAsString(comparisonValue);
    return entryValue === comparisonValue;
  } catch (error) {
    console.warn("Error comparing values for equality:", error);
    return false;
  }
}

/**
 * Checks if two values are not equal after conversion to strings.
 *
 * @param entryValue - First value to compare
 * @param comparisonValue - Second value to compare
 * @returns True if the string representations are not equal
 */
export function valueIsNotEqual(entryValue: any, comparisonValue: any): boolean {
  try {
    entryValue = getOriginalValueAsString(entryValue);
    comparisonValue = getOriginalValueAsString(comparisonValue);
    return entryValue !== comparisonValue;
  } catch (error) {
    console.warn("Error comparing values for inequality:", error);
    return false;
  }
}

/**
 * Base comparison function that applies a comparator to prepared values.
 * Ensures that comparison is only done if both values are dates or both values are numbers.
 *
 * @param entryValue - First value to compare
 * @param comparisonValue - Second value to compare
 * @param comparator - Function that defines the comparison logic
 * @returns Result of the comparison, or false if values cannot be compared
 */
export function compareValues(
  entryValue: any,
  comparisonValue: any,
  comparator: (a: any, b: any) => boolean
): boolean {
  try {
    if (bothDates(entryValue, comparisonValue) ||
        (isNumeric(entryValue) && isNumeric(comparisonValue))) {
      const [preparedEntry, preparedComparison] = prepareValues(entryValue, comparisonValue);

      // Ensure we have valid values to compare
      if (preparedEntry === null || preparedComparison === null) {
        return false;
      }

      return comparator(preparedEntry, preparedComparison);
    }
  } catch (error) {
    console.warn("Error comparing values:", error);
  }
  return false;
}

/**
 * Checks if the first value is less than or equal to the second value.
 *
 * @param entryValue - First value to compare
 * @param comparisonValue - Second value to compare
 * @returns True if entryValue ≤ comparisonValue
 */
export function valueIsSmallerOrEqual(entryValue: any, comparisonValue: any): boolean {
  return compareValues(entryValue, comparisonValue, (a, b) => a <= b);
}

/**
 * Checks if the first value is greater than or equal to the second value.
 *
 * @param entryValue - First value to compare
 * @param comparisonValue - Second value to compare
 * @returns True if entryValue ≥ comparisonValue
 */
export function valueIsGreaterOrEqual(entryValue: any, comparisonValue: any): boolean {
  return compareValues(entryValue, comparisonValue, (a, b) => a >= b);
}

/**
 * Checks if the first value is less than the second value.
 *
 * @param entryValue - First value to compare
 * @param comparisonValue - Second value to compare
 * @returns True if entryValue < comparisonValue
 */
export function valueIsSmaller(entryValue: any, comparisonValue: any): boolean {
  return compareValues(entryValue, comparisonValue, (a, b) => a < b);
}

/**
 * Checks if the first value is greater than the second value.
 *
 * @param entryValue - First value to compare
 * @param comparisonValue - Second value to compare
 * @returns True if entryValue > comparisonValue
 */
export function valueIsGreater(entryValue: any, comparisonValue: any): boolean {
  return compareValues(entryValue, comparisonValue, (a, b) => a > b);
}

/**
 * Removes all matches of a regular expression from a string value.
 *
 * @param entryValue - The value to process
 * @param comparisonValue - Regular expression pattern as string
 * @returns String with matches removed, or original string if an error occurs
 */
export function regexDeleteMatch(entryValue: any, comparisonValue: string): string {
  const originalValue = getOriginalValueAsString(entryValue);
  const comparisonRegExp = RegExp(comparisonValue, 'g');
  return originalValue.replaceAll(comparisonRegExp, '');
}

/**
 * Replaces all matches of a regular expression with a replacement value.
 *
 * @param entryValue - The value to process
 * @param comparisonValue - Regular expression pattern as string
 * @param replacementValue - String to replace matches with
 * @returns String with replacements, or original string if an error occurs
 */
export function regexReplaceMatch(
  entryValue: any,
  comparisonValue: string,
  replacementValue: string
): string {
  const originalValue = getOriginalValueAsString(entryValue);
  const comparisonRegExp = RegExp(comparisonValue, 'g');
  return originalValue.replaceAll(comparisonRegExp, replacementValue);
}

/**
 * Tests if a string value matches a regular expression pattern.
 * Used to determine if a row should be deleted.
 *
 * @param entryValue - The value to test
 * @param comparisonValue - Regular expression pattern as string
 * @returns True if the pattern matches, false otherwise or if an error occurs
 */
export function regexDeleteRow(entryValue: any, comparisonValue: string): boolean {
  const originalValue = getOriginalValueAsString(entryValue);
  const comparisonRegExp = RegExp(comparisonValue, 'g');
  return comparisonRegExp.test(originalValue);
}

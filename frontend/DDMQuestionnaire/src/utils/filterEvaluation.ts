/**
 * Checks whether a value represents an integer.
 *
 * - For strings: matches only well-formed integer literals (optional
 *   leading '-', no leading zeros other than a bare '0', no decimal point).
 *   Leading-zero strings like "0234" are rejected on purpose, since they're
 *   ambiguous/malformed as plain decimal integers.
 * - For numbers: delegates to `Number.isInteger`.
 * - Anything else (including non-numeric strings) returns false.
 */
function isInt(value: unknown): boolean {
  if (typeof value === 'number') return Number.isInteger(value);
  if (typeof value === 'string') return /^-?(0|[1-9]\d*)$/.test(value);
  return false;
}

/**
 * Checks whether a value represents a float (or an integer, which counts
 * as a valid float).
 *
 * - For strings: matches well-formed decimal literals, e.g. "123", "234.34".
 *   Rejects leading zeros ("0234"), and rejects malformed strings with more
 *   than one decimal point ("123.123.123").
 * - For numbers: delegates to `Number.isFinite`.
 * - Anything else returns false.
 */
function isFloat(value: unknown): boolean {
  if (typeof value === 'number') return Number.isFinite(value);
  if (typeof value === 'string') return /^-?(0|[1-9]\d*)(\.\d+)?$/.test(value);
  return false;
}

type FilterValueType = 'numeric' | 'string';

/**
 * Classifies a value's effective type for filter-comparison purposes.
 * - Numbers: 'numeric' if finite, 'string' if NaN/Infinity (treated
 *   conservatively as non-numeric).
 * - Strings: 'numeric' if they match a well-formed int or float literal,
 *   otherwise 'string'.
 * - Anything else (null, undefined, boolean, object, ...): 'string',
 *   the most conservative bucket — never silently coerced to a number.
 */
function typeOf(value: unknown): FilterValueType {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? 'numeric' : 'string';
  }
  if (typeof value === 'string') {
    return isInt(value) || isFloat(value) ? 'numeric' : 'string';
  }
  return 'string';
}

/**
 * Coerces two values for comparison according to their combined type:
 * - both numeric -> Number(...) on both sides (numeric compare)
 * - either side non-numeric -> String(...) on both sides (the more
 *   conservative type wins)
 */
function coercePair(valueLeft: unknown, valueRight: unknown): [unknown, unknown] {
  const bothNumeric = typeOf(valueLeft) === 'numeric' && typeOf(valueRight) === 'numeric';

  return bothNumeric
    ? [Number(valueLeft), Number(valueRight)]
    : [String(valueLeft), String(valueRight)];
}

/**
 * Evaluates a comparison between two values using the provided operator.
 *
 * Numeric-looking strings (e.g. "123", "234.34") are coerced to actual
 * numbers before comparison, so that e.g. "10" > "9" behaves numerically
 * (true) rather than lexicographically (false, since "1" < "9" as strings).
 * Non-numeric strings are left as-is.
 *
 * Supported operators:
 * - Equality: '==', '!='
 * - Numeric: '>', '<', '>=', '<='
 * - String: 'contains', 'contains_not'
 *
 * @param {*} valueLeft - The left-hand operand in the comparison.
 * @param {*} valueRight - The right-hand operand in the comparison.
 * @param {string} operator - The comparison operator to apply.
 * @returns {boolean} The result of the comparison.
 *
 * @throws {Error} If the operator is not recognized.
 */
export function evaluateFilter(valueLeft: unknown, valueRight: unknown, operator: string): boolean {
  const [left, right] = coercePair(valueLeft, valueRight);

  switch (operator) {
    case '==':
      return left === right;
    case '!=':
      return left !== right;
    case '>':
      return left > right;
    case '<':
      return left < right;
    case '>=':
      return left >= right;
    case '<=':
      return left <= right;
    case 'contains':
      return String(valueLeft).includes(String(valueRight));
    case 'contains_not':
      return !String(valueLeft).includes(String(valueRight));
    default:
      throw new Error(`Invalid operator: ${operator}`);
  }
}

/**
 * Evaluates a logical filter chain array, respecting operator precedence.
 *
 * The input array must alternate between boolean values and logical operators,
 * e.g. [true, 'AND', false, 'OR', true].
 *
 * - Resolves all 'AND' operations first (higher precedence).
 * - Then resolves remaining values with 'OR'.
 *
 * @param {Array<boolean|string>} arr - The logical expression array to evaluate.
 * @returns {boolean} The result of evaluating the full logical expression.
 */
export function evaluateFilterChain(arr: Array<boolean | 'AND' | 'OR'>): boolean {
  // Step 1: Resolve all AND operations first.
  const intermediate: boolean[] = [];
  let i = 0;

  while (i < arr.length) {
    const current = arr[i];

    if (current === 'AND') {
      const prev = intermediate.pop(); // Take last value
      const next = arr[i + 1] as boolean; // Take next value
      intermediate.push(prev && next); // Evaluate AND
      i += 2; // Skip the next value since it's already used
    } else if (current === 'OR') {
      i++;  // skip OR here, will resolve later
    } else {
      intermediate.push(current);
      i++;
    }
  }

  // Step 2: Resolve OR operations
  if (intermediate.length === 0) return false;
  return intermediate.reduce((acc, curr) => acc || curr);
}

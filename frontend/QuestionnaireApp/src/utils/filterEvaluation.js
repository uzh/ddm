/**
 * Evaluates a comparison between two values using the provided operator.
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
export function evaluateFilter(valueLeft, valueRight, operator) {
  switch (operator) {
    case '==':
      return valueLeft == valueRight;
    case '!=':
      return valueLeft != valueRight;
    case '>':
      return valueLeft > valueRight;
    case '<':
      return valueLeft < valueRight;
    case '>=':
      return valueLeft >= valueRight;
    case '<=':
      return valueLeft <= valueRight;
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
export function evaluateFilterChain(arr) {
  // Step 1: Resolve all AND operations first.
  const intermediate = [];
  let i = 0;

  while (i < arr.length) {
    if (arr[i] === 'AND') {
      const prev = intermediate.pop(); // Take last value
      const next = arr[i + 1]; // Take next value
      intermediate.push(prev && next); // Evaluate AND
      i += 2; // Skip the next value since it's already used
    } else {
      intermediate.push(arr[i]);
      i++;
    }
  }

  // Step 2: Resolve OR operations
  if (intermediate.length === 0) return false;
  return intermediate.reduce((acc, curr) => acc || curr);
}

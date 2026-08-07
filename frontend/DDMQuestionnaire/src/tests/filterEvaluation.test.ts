// src/utils/filterEvaluation.test.ts
import { describe, it, expect } from 'vitest';
import { evaluateFilter, evaluateFilterChain } from '@questionnaire/utils/filterEvaluation';

describe('evaluateFilter', () => {
  describe('equality operators (==, !=)', () => {
    it('treats equal numbers as equal', () => {
      expect(evaluateFilter(5, 5, '==')).toBe(true);
      expect(evaluateFilter(5, 6, '==')).toBe(false);
    });

    it('coerces numeric strings before comparing', () => {
      expect(evaluateFilter('5', 5, '==')).toBe(true);
      expect(evaluateFilter('5', '5', '==')).toBe(true);
      expect(evaluateFilter('5.0', 5, '==')).toBe(true); // "5.0" is a well-formed float string, coerces to 5, equals 5
    });

    it('does not coerce when one side is non-numeric', () => {
      expect(evaluateFilter('abc', 'abc', '==')).toBe(true);
      expect(evaluateFilter('5', 'abc', '==')).toBe(false);
      expect(evaluateFilter(5, 'abc', '==')).toBe(false);
    });

    it('!= is the negation of ==', () => {
      expect(evaluateFilter(5, 6, '!=')).toBe(true);
      expect(evaluateFilter(5, 5, '!=')).toBe(false);
    });
  });

  describe('numeric comparison operators (>, <, >=, <=)', () => {
    it('compares numerically, not lexicographically, for numeric strings', () => {
      expect(evaluateFilter('10', '9', '>')).toBe(true); // would be false as string comparison
      expect(evaluateFilter('9', '10', '<')).toBe(true);
    });

    it('handles int vs float comparisons correctly', () => {
      expect(evaluateFilter(23, 23.5, '<')).toBe(true);
      expect(evaluateFilter('23', '23.5', '<')).toBe(true);
      expect(evaluateFilter(23, 22.9, '>')).toBe(true);
    });

    it('falls back to string comparison when either side is non-numeric', () => {
      // 'b' > 'a' lexicographically
      expect(evaluateFilter('b', 'a', '>')).toBe(true);
    });

    it('supports >= and <= at the boundary', () => {
      expect(evaluateFilter(5, 5, '>=')).toBe(true);
      expect(evaluateFilter(5, 5, '<=')).toBe(true);
      expect(evaluateFilter(4, 5, '>=')).toBe(false);
    });
  });

  describe('contains / contains_not', () => {
    it('checks substring containment on the original (uncoerced) values', () => {
      expect(evaluateFilter('hello world', 'world', 'contains')).toBe(true);
      expect(evaluateFilter('hello world', 'xyz', 'contains')).toBe(false);
    });

    it('contains_not negates contains', () => {
      expect(evaluateFilter('hello world', 'xyz', 'contains_not')).toBe(true);
      expect(evaluateFilter('hello world', 'world', 'contains_not')).toBe(false);
    });

    it('stringifies non-string operands for containment checks', () => {
      expect(evaluateFilter(12345, '234', 'contains')).toBe(true);
    });
  });

  describe('numeric string edge cases (leading zeros, malformed floats)', () => {
    it('treats leading-zero strings as non-numeric (compared as strings)', () => {
      // "0234" is NOT considered numeric per isInt/isFloat, so both sides
      // fall back to string comparison.
      expect(evaluateFilter('0234', 234, '==')).toBe(false); // "0234" !== "234" as strings
      expect(evaluateFilter('0234', '0234', '==')).toBe(true); // identical strings still equal
    });

    it('treats malformed multi-dot floats as non-numeric', () => {
      expect(evaluateFilter('123.123.123', '123.123.123', '==')).toBe(true); // equal as strings
      expect(evaluateFilter('123.123.123', 123, '==')).toBe(false); // string vs number, not coerced
    });

    it('coerces well-formed float strings', () => {
      expect(evaluateFilter('234.34', 234.34, '==')).toBe(true);
    });
  });

  describe('non-numeric, non-string inputs (null, undefined, boolean)', () => {
    it('treats null/undefined/boolean as the conservative string bucket', () => {
      expect(evaluateFilter(null, null, '==')).toBe(true); // String(null) === String(null)
      expect(evaluateFilter(undefined, undefined, '==')).toBe(true);
      expect(evaluateFilter(true, true, '==')).toBe(true);
      expect(evaluateFilter(true, 1, '==')).toBe(false); // boolean side forces string comparison: "true" !== "1"
    });
  });

  describe('NaN / Infinity', () => {
    it('treats NaN and Infinity as non-numeric', () => {
      expect(evaluateFilter(NaN, NaN, '==')).toBe(true); // String(NaN) === String(NaN) -> "NaN" === "NaN"
      expect(evaluateFilter(Infinity, Infinity, '==')).toBe(true); // "Infinity" === "Infinity"
      expect(evaluateFilter(Infinity, 5, '==')).toBe(false);
    });
  });

  describe('invalid operator', () => {
    it('throws for an unrecognized operator', () => {
      expect(() => evaluateFilter(1, 2, 'nonsense')).toThrow('Invalid operator: nonsense');
    });
  });
});

describe('evaluateFilterChain', () => {
  it('returns false for an empty array', () => {
    expect(evaluateFilterChain([])).toBe(false);
  });

  it('evaluates a single boolean with no operators', () => {
    expect(evaluateFilterChain([true])).toBe(true);
    expect(evaluateFilterChain([false])).toBe(false);
  });

  it('resolves a simple AND', () => {
    expect(evaluateFilterChain([true, 'AND', true])).toBe(true);
    expect(evaluateFilterChain([true, 'AND', false])).toBe(false);
  });

  it('resolves a simple OR', () => {
    expect(evaluateFilterChain([false, 'OR', true])).toBe(true);
    expect(evaluateFilterChain([false, 'OR', false])).toBe(false);
  });

  it('gives AND higher precedence than OR', () => {
    // false OR (true AND false) = false OR false = false
    expect(evaluateFilterChain([false, 'OR', true, 'AND', false])).toBe(false);

    // true OR (false AND false) = true OR false = true
    expect(evaluateFilterChain([true, 'OR', false, 'AND', false])).toBe(true);

    // (true AND false) OR true = false OR true = true
    expect(evaluateFilterChain([true, 'AND', false, 'OR', true])).toBe(true);
  });

  it('resolves a longer mixed chain correctly', () => {
    // true AND true OR false AND false OR true
    // -> (true AND true) OR (false AND false) OR true
    // -> true OR false OR true
    // -> true
    expect(
      evaluateFilterChain([true, 'AND', true, 'OR', false, 'AND', false, 'OR', true])
    ).toBe(true);
  });

  it('resolves an all-false chain to false', () => {
    expect(evaluateFilterChain([false, 'OR', false, 'AND', false])).toBe(false);
  });

  it('resolves multiple consecutive ANDs', () => {
    expect(evaluateFilterChain([true, 'AND', true, 'AND', true])).toBe(true);
    expect(evaluateFilterChain([true, 'AND', true, 'AND', false])).toBe(false);
  });
});

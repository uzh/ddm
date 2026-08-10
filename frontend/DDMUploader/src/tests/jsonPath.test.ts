import { describe, it, expect } from 'vitest';
import {
  getNestedJsonContent,
  resolveNestedCollection,
  joinIfPrimitiveArray,
} from '@uploader/composables/useFileProcessor/jsonPath';

describe('getNestedJsonContent', () => {
  it('resolves a dot-notation path', () => {
    const obj = { a: { b: { c: 'value' } } };
    expect(getNestedJsonContent(obj, 'a.b.c')).toBe('value');
  });

  it('resolves a bracket-notation path', () => {
    const obj = { a: { b: 'value' } };
    expect(getNestedJsonContent(obj, 'a[b]')).toBe('value');
  });

  it('returns undefined for a missing path segment', () => {
    const obj = { a: { b: 'value' } };
    expect(getNestedJsonContent(obj, 'a.missing.c')).toBeUndefined();
  });
});

describe('resolveNestedCollection', () => {
  it('returns an array node as-is', () => {
    const rootItem = { items: [{ id: 1 }, { id: 2 }] };
    expect(resolveNestedCollection(rootItem, 'items')).toEqual([{ id: 1 }, { id: 2 }]);
  });

  it('returns the values of an object node, discarding keys', () => {
    const rootItem = { mapping: { 'uuid-1': { id: 'uuid-1' }, 'uuid-2': { id: 'uuid-2' } } };
    expect(resolveNestedCollection(rootItem, 'mapping')).toEqual([
      { id: 'uuid-1' },
      { id: 'uuid-2' },
    ]);
  });

  it('returns an empty array when the path does not resolve', () => {
    const rootItem = { other: 'value' };
    expect(resolveNestedCollection(rootItem, 'mapping')).toEqual([]);
  });

  it('returns an empty array when the resolved node is a primitive', () => {
    const rootItem = { mapping: 'not-an-object' };
    expect(resolveNestedCollection(rootItem, 'mapping')).toEqual([]);
  });

  it('returns an empty array when nestedLoopPath is empty', () => {
    const rootItem = { mapping: { a: 1 } };
    expect(resolveNestedCollection(rootItem, '')).toEqual([]);
  });
});

describe('joinIfPrimitiveArray', () => {
  it('joins an array of strings using the given separator', () => {
    expect(joinIfPrimitiveArray(['a', 'b', 'c'], ', ')).toBe('a, b, c');
  });

  it('joins a single-element array trivially', () => {
    expect(joinIfPrimitiveArray(['solo'], '\n')).toBe('solo');
  });

  it('treats null elements as empty strings when joining', () => {
    expect(joinIfPrimitiveArray(['a', null, 'c'], '-')).toBe('a--c');
  });

  it('returns non-array values unchanged', () => {
    expect(joinIfPrimitiveArray('plain string', '\n')).toBe('plain string');
    expect(joinIfPrimitiveArray(42, '\n')).toBe(42);
  });

  it('returns an array containing non-primitive elements unchanged', () => {
    const value = [{ nested: true }, 'mixed'];
    expect(joinIfPrimitiveArray(value, '\n')).toBe(value);
  });

  it('returns an empty array unchanged', () => {
    expect(joinIfPrimitiveArray([], '\n')).toEqual([]);
  });
});

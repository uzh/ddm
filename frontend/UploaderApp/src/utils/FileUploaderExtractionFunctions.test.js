import { expect, test } from 'vitest'
import {
  valueIsEqual,
  valueIsNotEqual,
  valueIsSmallerOrEqual,
  valueIsGreaterOrEqual,
  valueIsSmaller,
  valueIsGreater,
  regexDeleteMatch,
  regexReplaceMatch,
  regexDeleteRow
} from './FileUploaderExtractionFunctions'

test('valueIsEqual', () => {
  expect(valueIsEqual(1, 1)).toBe(true);
  expect(valueIsEqual(1, '1')).toBe(true);
  expect(valueIsEqual('1', 1)).toBe(true);
  expect(valueIsEqual('1', '1')).toBe(true);

  expect(valueIsEqual('abc', 'abc')).toBe(true);
  expect(valueIsEqual([1,2], '[1,2]')).toBe(true);
  expect(valueIsEqual([1,2], [1,2])).toBe(true);

  expect(valueIsEqual('2016-05-25T092415.123', '2016-05-25T092415.123')).toBe(true);

  expect(valueIsEqual(1, 2)).toBe(false);
  expect(valueIsEqual('1', '2')).toBe(false);
  expect(valueIsEqual(1, '2')).toBe(false);
  expect(valueIsEqual('1', 2)).toBe(false);

  expect(valueIsEqual('abc', 'acb')).toBe(false);
  expect(valueIsEqual([1,2], '[2,1]')).toBe(false);
  expect(valueIsEqual([1,2], [1,3])).toBe(false);

  expect(valueIsEqual('2016-05-25T092415.123', '2016-05-25T092410.123')).toBe(false);
})

test('valueIsNotEqual', () => {
  expect(valueIsNotEqual(1, 1)).toBe(false);
  expect(valueIsNotEqual(1, '1')).toBe(false);
  expect(valueIsNotEqual('1', 1)).toBe(false);
  expect(valueIsNotEqual('1', '1')).toBe(false);

  expect(valueIsNotEqual('abc', 'abc')).toBe(false);
  expect(valueIsNotEqual([1,2], '[1,2]')).toBe(false);
  expect(valueIsNotEqual([1,2], [1,2])).toBe(false);

  expect(valueIsNotEqual('2016-05-25T092415.123', '2016-05-25T092415.123')).toBe(false);

  expect(valueIsNotEqual(1, 2)).toBe(true);
  expect(valueIsNotEqual(1, '2')).toBe(true);
  expect(valueIsNotEqual('1', 2)).toBe(true);
  expect(valueIsNotEqual('1', '2')).toBe(true);

  expect(valueIsNotEqual('abc', 'acb')).toBe(true);
  expect(valueIsNotEqual([1,2], '[2,1]')).toBe(true);
  expect(valueIsNotEqual([1,2], [1,3])).toBe(true);

  expect(valueIsNotEqual('2016-05-25T092415.123', '2016-05-25T092410.123')).toBe(true);
})

test('valueIsSmallerOrEqual', () => {
  expect(valueIsSmallerOrEqual(1, 1)).toBe(true);
  expect(valueIsSmallerOrEqual(1, 2)).toBe(true);
  expect(valueIsSmallerOrEqual('1', '1')).toBe(true);
  expect(valueIsSmallerOrEqual('1', '2')).toBe(true);

  expect(valueIsSmallerOrEqual(1, '1')).toBe(true);
  expect(valueIsSmallerOrEqual(1, '2')).toBe(true);
  expect(valueIsSmallerOrEqual('1', 1)).toBe(true);
  expect(valueIsSmallerOrEqual('1', 2)).toBe(true);

  expect(valueIsSmallerOrEqual('2016-05-25T092415.123', '2016-05-25T092415.123')).toBe(true);
  expect(valueIsSmallerOrEqual('2016-05-24T092415.123', '2016-05-25T092415.123')).toBe(true);
  expect(valueIsSmallerOrEqual('Tue, 01 Nov 2016 13:23:12 +0630', 'Tue, 01 Nov 2016 13:23:12 +0630')).toBe(true);
  expect(valueIsSmallerOrEqual('Tue, 01 Nov 2016 13:23:12 +0630', 'Wed, 02 Nov 2016 13:23:12 +0630')).toBe(true);
  expect(valueIsSmallerOrEqual('Sunday, 06-Nov-94 08:49:37 GMT', 'Sunday, 06-Nov-94 08:49:37 GMT')).toBe(true);
  expect(valueIsSmallerOrEqual('Saturday, 05-Nov-94 08:49:37 GMT', 'Sunday, 06-Nov-94 08:49:37 GMT')).toBe(true);


  expect(valueIsSmallerOrEqual(2, 1)).toBe(false);
  expect(valueIsSmallerOrEqual('2', '1')).toBe(false);
  expect(valueIsSmallerOrEqual(2, '1')).toBe(false);
  expect(valueIsSmallerOrEqual('2', 1)).toBe(false);

  expect(valueIsSmallerOrEqual('2016-05-25T092415.123', '2016-05-24T092415.123')).toBe(false);
  expect(valueIsSmallerOrEqual('2016-05-25T092415.123', '2016-05-25T092410.123')).toBe(false);
  expect(valueIsSmallerOrEqual('Wed, 02 Nov 2016 13:23:12 +0630', 'Tue, 01 Nov 2016 13:23:12 +0630')).toBe(false);
  expect(valueIsSmallerOrEqual('Sunday, 06-Nov-94 08:49:37 GMT', 'Saturday, 05-Nov-94 08:49:37 GMT')).toBe(false);

  expect(valueIsSmallerOrEqual('abc', 'abc')).toBe(false);
  expect(valueIsSmallerOrEqual('abc', 'acb')).toBe(false);
  expect(valueIsSmallerOrEqual([1,2], '[1,2]')).toBe(false);
  expect(valueIsSmallerOrEqual([1,2], [1,2])).toBe(false);
})

test('valueIsGreaterOrEqual', () => {
  expect(valueIsGreaterOrEqual(1, 1)).toBe(true);
  expect(valueIsGreaterOrEqual(1, '1')).toBe(true);
  expect(valueIsGreaterOrEqual('1', 1)).toBe(true);
  expect(valueIsGreaterOrEqual('1', '1')).toBe(true);

  expect(valueIsGreaterOrEqual(2, 1)).toBe(true);
  expect(valueIsGreaterOrEqual(2, '1')).toBe(true);
  expect(valueIsGreaterOrEqual('2', 1)).toBe(true);
  expect(valueIsGreaterOrEqual('2', '1')).toBe(true);

  expect(valueIsGreaterOrEqual('2016-05-25T092415.123', '2016-05-24T092415.123')).toBe(true);
  expect(valueIsGreaterOrEqual('2016-05-25T092415.123', '2016-05-25T092410.123')).toBe(true);
  expect(valueIsGreaterOrEqual('Wed, 02 Nov 2016 13:23:12 +0630', 'Tue, 01 Nov 2016 13:23:12 +0630')).toBe(true);
  expect(valueIsGreaterOrEqual('Tue, 01 Nov 2016 13:23:12 +0630', 'Tue, 01 Nov 2016 13:23:12 +0630')).toBe(true);
  expect(valueIsGreaterOrEqual('Saturday, 05-Nov-94 08:49:37 GMT', 'Saturday, 05-Nov-94 08:49:37 GMT')).toBe(true);
  expect(valueIsGreaterOrEqual('Sunday, 06-Nov-94 08:49:37 GMT', 'Saturday, 05-Nov-94 08:49:37 GMT')).toBe(true);

  expect(valueIsGreaterOrEqual(1, 2)).toBe(false);
  expect(valueIsGreaterOrEqual('1', '2')).toBe(false);
  expect(valueIsGreaterOrEqual(1, '2')).toBe(false);
  expect(valueIsGreaterOrEqual('1', 2)).toBe(false);

  expect(valueIsGreaterOrEqual('2016-05-24T092415.123', '2016-05-25T092415.123')).toBe(false);
  expect(valueIsGreaterOrEqual('Tue, 01 Nov 2016 13:23:12 +0630', 'Wed, 02 Nov 2016 13:23:12 +0630')).toBe(false);
  expect(valueIsGreaterOrEqual('Saturday, 05-Nov-94 08:49:37 GMT', 'Sunday, 06-Nov-94 08:49:37 GMT')).toBe(false);

  expect(valueIsGreaterOrEqual('abc', 'abc')).toBe(false);
  expect(valueIsGreaterOrEqual('abc', 'acb')).toBe(false);
  expect(valueIsGreaterOrEqual([1,2], '[1,2]')).toBe(false);
  expect(valueIsGreaterOrEqual([1,2], [1,2])).toBe(false);
})

test('valueIsSmaller', () => {
  expect(valueIsSmaller(1, 2)).toBe(true);
  expect(valueIsSmaller('1', '2')).toBe(true);
  expect(valueIsSmaller(1, '2')).toBe(true);
  expect(valueIsSmaller('1', 2)).toBe(true);

  expect(valueIsSmaller('2016-05-24T092415.123', '2016-05-25T092415.123')).toBe(true);
  expect(valueIsSmaller('Tue, 01 Nov 2016 13:23:12 +0630', 'Wed, 02 Nov 2016 13:23:12 +0630')).toBe(true);
  expect(valueIsSmaller('Saturday, 05-Nov-94 08:49:37 GMT', 'Sunday, 06-Nov-94 08:49:37 GMT')).toBe(true);


  expect(valueIsSmaller(1, 1)).toBe(false);
  expect(valueIsSmaller(1, '1')).toBe(false);
  expect(valueIsSmaller('1', 1)).toBe(false);
  expect(valueIsSmaller('1', '1')).toBe(false);

  expect(valueIsSmaller(2, 1)).toBe(false);
  expect(valueIsSmaller('2', '1')).toBe(false);
  expect(valueIsSmaller(2, '1')).toBe(false);
  expect(valueIsSmaller('2', 1)).toBe(false);

  expect(valueIsSmaller('2016-05-25T092415.123', '2016-05-25T092415.123')).toBe(false);
  expect(valueIsSmaller('2016-05-25T092415.123', '2016-05-24T092415.123')).toBe(false);
  expect(valueIsSmaller('2016-05-25T092415.123', '2016-05-25T092410.123')).toBe(false);
  expect(valueIsSmaller('Tue, 01 Nov 2016 13:23:12 +0630', 'Tue, 01 Nov 2016 13:23:12 +0630')).toBe(false);
  expect(valueIsSmaller('Wed, 02 Nov 2016 13:23:12 +0630', 'Tue, 01 Nov 2016 13:23:12 +0630')).toBe(false);
  expect(valueIsSmaller('Sunday, 06-Nov-94 08:49:37 GMT', 'Sunday, 06-Nov-94 08:49:37 GMT')).toBe(false);
  expect(valueIsSmaller('Sunday, 06-Nov-94 08:49:37 GMT', 'Saturday, 05-Nov-94 08:49:37 GMT')).toBe(false);

  expect(valueIsSmaller('abc', 'abc')).toBe(false);
  expect(valueIsSmaller('abc', 'acb')).toBe(false);
  expect(valueIsSmaller([1,2], '[1,2]')).toBe(false);
  expect(valueIsSmaller([1,2], [1,2])).toBe(false);
})

test('valueIsGreater', () => {
  expect(valueIsGreater(1, 2)).toBe(false);
  expect(valueIsGreater('1', '2')).toBe(false);
  expect(valueIsGreater(1, '2')).toBe(false);
  expect(valueIsGreater('1', 2)).toBe(false);

  expect(valueIsGreater('2016-05-25T092415.123', '2016-05-25T092415.123')).toBe(false);
  expect(valueIsGreater('2016-05-24T092415.123', '2016-05-25T092415.123')).toBe(false);
  expect(valueIsGreater('Tue, 01 Nov 2016 13:23:12 +0630', 'Tue, 01 Nov 2016 13:23:12 +0630')).toBe(false);
  expect(valueIsGreater('Tue, 01 Nov 2016 13:23:12 +0630', 'Wed, 02 Nov 2016 13:23:12 +0630')).toBe(false);
  expect(valueIsGreater('Sunday, 06-Nov-94 08:49:37 GMT', 'Sunday, 06-Nov-94 08:49:37 GMT')).toBe(false);
  expect(valueIsGreater('Saturday, 05-Nov-94 08:49:37 GMT', 'Sunday, 06-Nov-94 08:49:37 GMT')).toBe(false);


  expect(valueIsGreater(1, 1)).toBe(false);
  expect(valueIsGreater(1, '1')).toBe(false);
  expect(valueIsGreater('1', 1)).toBe(false);
  expect(valueIsGreater('1', '1')).toBe(false);

  expect(valueIsGreater(2, 1)).toBe(true);
  expect(valueIsGreater('2', '1')).toBe(true);
  expect(valueIsGreater(2, '1')).toBe(true);
  expect(valueIsGreater('2', 1)).toBe(true);

  expect(valueIsGreater('2016-05-25T092415.123', '2016-05-24T092415.123')).toBe(true);
  expect(valueIsGreater('2016-05-25T092415.123', '2016-05-25T092410.123')).toBe(true);
  expect(valueIsGreater('Wed, 02 Nov 2016 13:23:12 +0630', 'Tue, 01 Nov 2016 13:23:12 +0630')).toBe(true);
  expect(valueIsGreater('Sunday, 06-Nov-94 08:49:37 GMT', 'Saturday, 05-Nov-94 08:49:37 GMT')).toBe(true);

  expect(valueIsGreater('abc', 'abc')).toBe(false);
  expect(valueIsGreater('abc', 'acb')).toBe(false);
  expect(valueIsGreater([1,2], '[1,2]')).toBe(false);
  expect(valueIsGreater([1,2], [1,2])).toBe(false);
})

test('regexDeleteMatch', () => {
  expect(regexDeleteMatch('abc', 'a')).toBe('bc');
  expect(regexDeleteMatch([1,2], '\\[')).toBe('1,2]');
  expect(regexDeleteMatch('some string with email@address.com in the middle', 'email@address\.com')).toBe('some string with  in the middle');
})

test('regexReplaceMatch', () => {
  expect(regexReplaceMatch('abc', 'a', 'd')).toBe('dbc');
  expect(regexReplaceMatch([1,2], '\\[', 'd')).toBe('d1,2]');
  expect(regexReplaceMatch('some string with email@address.com in the middle', 'email@address\.com', 'anonymized')).toBe('some string with anonymized in the middle');
})

test('regexDeleteRow', () => {
  expect(regexDeleteRow('abc', 'a')).toBe(true);
  expect(regexDeleteRow([1,2], '^\\[')).toBe(true);
  expect(regexDeleteRow([1,2], '^.\\[')).toBe(false);
  expect(regexDeleteRow('some string with email@address.com in the middle', 'email@address\.com')).toBe(true);
})

import { describe, it, expect } from 'vitest';
import { extractData, getKeyMap } from '@uploader/composables/useFileProcessor/extractionEngine';
import { useFileProcessor } from '@uploader/composables/useFileProcessor';
import { BlueprintExtractionOutcome } from '@uploader/classes/BlueprintExtractionOutcome';
import { Blueprint } from '@uploader/types/Blueprint';
import { ExtractionRule } from '@uploader/types/ExtractionRule';
import messageData from './fixtures/MessageData.json';

const CHAT_PATTERN = '^test:chat:.*';
const FIRST_CHAT_KEY = 'test:chat:792179ee83d1';

// Keeps only messages that are exactly a "test:<type>:<id>" URI; replaces all other message texts.
const REDACT_NON_URI_MESSAGES = '("message":")(?!test:[a-z-]+:[A-Za-z0-9]+")(?:[^"\\\\]|\\\\.)*(")';

function rule(overrides: Partial<ExtractionRule>): ExtractionRule {
  return {
    id: 1,
    field: 'name',
    regex_field: false,
    comparison_operator: null,
    comparison_value: null,
    replacement_value: null,
    ...overrides
  };
}

function makeBlueprint(rules: ExtractionRule[], overrides: Partial<Blueprint> = {}): Blueprint {
  return {
    id: 1,
    name: 'Test blueprint',
    description: '',
    format: 'json',
    json_extraction_root: '',
    expected_fields: [],
    exp_fields_regex_matching: false,
    fields_to_extract: [],
    regex_path: '.*\\.json',
    csv_delimiter: ',',
    extraction_rules: rules,
    ...overrides
  };
}

// Runs getKeyMap + extractData for one row and returns the extracted row (if any) and the outcome.
function extractRow(dataRow: Record<string, any>, rules: ExtractionRule[]) {
  const blueprint = makeBlueprint(rules);
  const outcomeMap = { [blueprint.id]: new BlueprintExtractionOutcome(blueprint) };
  const keyMap = getKeyMap(dataRow, rules, blueprint.id, outcomeMap);
  extractData(dataRow, rules, keyMap, blueprint.id, outcomeMap);
  return { extracted: outcomeMap[blueprint.id].extractedData[0], outcome: outcomeMap[blueprint.id] };
}

describe('regex-replace-match', () => {
  it('replaces matches in a field matched by an exact name', () => {
    const { extracted } = extractRow({ text: 'mail me at a@b.com' }, [
      rule({ id: 1, field: 'text' }),
      rule({ id: 2, field: 'text', comparison_operator: 'regex-replace-match',
            comparison_value: '[\\w.]+@[\\w.]+', replacement_value: '_anonymized_' })
    ]);
    expect(extracted.text).toBe('mail me at _anonymized_');
  });

  it('replaces matches in a field matched by a regex field', () => {
    const { extracted, outcome } = extractRow({ 'user_name': 'alice', 'user_mail': 'a@b.com' }, [
      rule({ id: 1, field: '^user_mail$', regex_field: true }),
      rule({ id: 2, field: '^user_mail$', regex_field: true, comparison_operator: 'regex-replace-match',
            comparison_value: '.+', replacement_value: '_removed_' })
    ]);
    expect(extracted['^user_mail$']).toBe('_removed_');
    expect(outcome.extractionRuleLog[2]).toBe(1);
  });

  it('does not change the field when the Replace rule precedes the Keep rule', () => {
    const { extracted } = extractRow({ text: 'secret' }, [
      rule({ id: 1, field: 'text', comparison_operator: 'regex-replace-match',
            comparison_value: 'secret', replacement_value: 'x' }),
      rule({ id: 2, field: 'text' })
    ]);
    expect(extracted.text).toBe('secret');
  });

  it('keeps the original value when the regex is invalid', () => {
    const { extracted } = extractRow({ text: 'secret' }, [
      rule({ id: 1, field: 'text' }),
      rule({ id: 2, field: 'text', comparison_operator: 'regex-replace-match',
            comparison_value: '(unclosed', replacement_value: 'x' })
    ]);
    expect(extracted.text).toBe('secret');
  });

  it('interprets $-sequences in the replacement value', () => {
    const { extracted } = extractRow({ text: 'john@example.com' }, [
      rule({ id: 1, field: 'text' }),
      rule({ id: 2, field: 'text', comparison_operator: 'regex-replace-match',
            comparison_value: '^[^@]+(@.+)$', replacement_value: '_$1_$$' })
    ]);
    expect(extracted.text).toBe('_@example.com_$');
  });

  it('applies the regex to the JSON text of non-string values', () => {
    const { extracted } = extractRow({ data: { a: 1 } }, [
      rule({ id: 1, field: 'data' }),
      rule({ id: 2, field: 'data', comparison_operator: 'regex-replace-match',
            comparison_value: '"a":1', replacement_value: '"a":0' })
    ]);
    expect(extracted.data).toBe('{"a":0}');
  });
});

describe('regex-delete-match', () => {
  it('deletes matches in a field matched by an exact name', () => {
    const { extracted } = extractRow({ text: 'Watched video XY' }, [
      rule({ id: 1, field: 'text' }),
      rule({ id: 2, field: 'text', comparison_operator: 'regex-delete-match', comparison_value: '^Watched ' })
    ]);
    expect(extracted.text).toBe('video XY');
  });

  it('deletes matches in a field matched by a regex field', () => {
    const { extracted } = extractRow({ text_a: 'Watched video XY' }, [
      rule({ id: 1, field: '^text_.$', regex_field: true }),
      rule({ id: 2, field: '^text_.$', regex_field: true, comparison_operator: 'regex-delete-match',
            comparison_value: '^Watched ' })
    ]);
    expect(extracted['^text_.$']).toBe('video XY');
  });
});

describe('regex-delete-row', () => {
  it('discards the row when a regex field value matches', () => {
    const { extracted, outcome } = extractRow({ text_a: 'Watched video XY' }, [
      rule({ id: 1, field: '^text_.$', regex_field: true }),
      rule({ id: 2, field: '^text_.$', regex_field: true, comparison_operator: 'regex-delete-row',
            comparison_value: '^Watched ' })
    ]);
    expect(extracted).toBeUndefined();
    expect(outcome.extractionStats.nRowsFilteredOut).toBe(1);
  });
});

describe('redacting chat messages (MessageData.json)', () => {
  const rules = [
    rule({ id: 1, field: CHAT_PATTERN, regex_field: true }),
    rule({ id: 2, field: CHAT_PATTERN, regex_field: true, comparison_operator: 'regex-replace-match',
          comparison_value: REDACT_NON_URI_MESSAGES, replacement_value: '$1_removed_$2' })
  ];

  function assertRedacted(chat: any) {
    const messages = chat.messages.map((m: any) => m.message);
    expect(messages).toEqual([
      '_removed_',
      'test:playlist:8f7da08c5f1a',
      '_removed_',
      'test:track:9d0f947aed4b',
      '_removed_'
    ]);
    // Everything except the message texts is untouched.
    const original = messageData[FIRST_CHAT_KEY];
    expect(chat.members).toEqual(original.members);
    expect(chat.messages.map((m: any) => m.uri)).toEqual(original.messages.map(m => m.uri));
  }

  it('redacts non-URI messages (unit)', () => {
    const { extracted } = extractRow(structuredClone(messageData), rules);
    // The rule's field matches both chats; only the first one is extracted (known limitation).
    const value = extracted[CHAT_PATTERN];
    expect(typeof value).toBe('string');
    assertRedacted(JSON.parse(value));
  });

  it('redacts non-URI messages (end to end via useFileProcessor)', async () => {
    const blueprint = makeBlueprint(rules, {
      expected_fields: [CHAT_PATTERN],
      exp_fields_regex_matching: true,
      fields_to_extract: [CHAT_PATTERN]
    });
    const file = new File([JSON.stringify(messageData)], 'MessageData.json', { type: 'application/json' });
    const processor = useFileProcessor(false, [blueprint]);
    await processor.handleSelectedFile(file);

    const extracted = processor.blueprintOutcomeMap[1].extractedData;
    expect(extracted.length).toBe(1);
    assertRedacted(JSON.parse(extracted[0][CHAT_PATTERN]));
  });
});

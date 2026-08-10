import { describe, it, expect } from 'vitest';
import { processContent } from '@uploader/composables/useFileProcessor/contentParsers';
import { BlueprintExtractionOutcome } from '@uploader/classes/BlueprintExtractionOutcome';
import { Blueprint } from '@uploader/types/Blueprint';
import { JSONParserConfig } from '@uploader/types/ParserConfigs';

// A trimmed ChatGPT-conversation-export-style fixture: the root is an array
// of "conversations", each with flat metadata plus a `mapping` field that is
// a JSON *object* (keyed by message UUID, not an array) holding the actual
// messages, several levels deep.
function buildChatExportContent(): string {
  return JSON.stringify([
    {
      conversation_id: 'conv-1',
      title: 'Spaghetti Recipe',
      mapping: {
        'msg-assistant': {
          id: 'msg-assistant',
          message: {
            author: { role: 'assistant' },
            content: { content_type: 'text', parts: ['Line1', 'Line2'] },
          },
          parent: 'msg-user',
        },
        'msg-user': {
          id: 'msg-user',
          message: {
            author: { role: 'user' },
            content: { content_type: 'text', parts: ['Spaghetti'] },
          },
          parent: 'client-created-root',
        },
        'client-created-root': {
          id: 'client-created-root',
          message: null,
          parent: null,
        },
        'orphan-entry': {
          id: 'orphan-entry',
          parent: null,
          // no `message` key at all -- should be caught by nested_expected_fields
        },
      },
    },
    {
      conversation_id: 'conv-2',
      title: 'No Mapping Here',
      // no `mapping` key at all -- nested_loop_path won't resolve for this item
    },
  ]);
}

function buildNestedBlueprint(): Blueprint {
  const parserConfig: JSONParserConfig = {
    format: 'json',
    extraction_root: '',
    nested_loop_path: 'mapping',
    array_join_separator: '\n',
  };

  return {
    id: 1,
    name: 'ChatGPT export',
    description: 'Tests two-level nested JSON extraction',
    format: 'json',
    parser_config: parserConfig,
    expected_fields: ['conversation_id'],
    exp_fields_regex_matching: false,
    nested_expected_fields: ['message'],
    nested_exp_fields_regex_matching: false,
    fields_to_extract: ['conversation_id', 'title', 'message_id', 'role', 'content'],
    extraction_fields: [
      { id: 1, scope: 'root', expected_name: 'conversation_id', match_regex: false, keep_in_donation: true, alias: null },
      { id: 2, scope: 'root', expected_name: 'title', match_regex: false, keep_in_donation: true, alias: null },
      { id: 3, scope: 'nested', expected_name: 'id', match_regex: false, keep_in_donation: true, alias: 'message_id' },
      { id: 4, scope: 'nested', expected_name: 'message.author.role', match_regex: false, keep_in_donation: true, alias: 'role' },
      { id: 5, scope: 'nested', expected_name: 'message.content.parts', match_regex: false, keep_in_donation: true, alias: 'content' },
    ],
    file_paths: [],
    extraction_rules: [],
    is_backup: false,
    backup_ids: [],
  };
}

describe('processContent — two-level nested JSON extraction', () => {
  it('extracts one row per nested message, merging root fields, joining array leaves, and skipping malformed items', () => {
    const blueprint = buildNestedBlueprint();
    const outcomeMap = { 1: new BlueprintExtractionOutcome(blueprint) };

    processContent(buildChatExportContent(), blueprint, outcomeMap);

    const outcome = outcomeMap[1];

    // Three rows: the two real messages, plus the null-message entry
    // (which passes the nested_expected_fields gate -- "message" is
    // present as a key, just null -- and still contributes its own "id"
    // field even though role/content can't be resolved from a null
    // message). The entry entirely missing "message" is excluded by the
    // nested required-field check instead.
    expect(outcome.extractedData.length).toBe(3);

    const byMessageId = Object.fromEntries(
      outcome.extractedData.map(row => [row.message_id, row])
    );

    expect(byMessageId['msg-user']).toEqual({
      conversation_id: 'conv-1',
      title: 'Spaghetti Recipe',
      message_id: 'msg-user',
      role: 'user',
      content: 'Spaghetti',
    });

    // content.parts (an array of two strings) is joined with the
    // configured array_join_separator.
    expect(byMessageId['msg-assistant']).toEqual({
      conversation_id: 'conv-1',
      title: 'Spaghetti Recipe',
      message_id: 'msg-assistant',
      role: 'assistant',
      content: 'Line1\nLine2',
    });

    // The null-message entry: "id" resolves (flat key), but "message.author.role"
    // and "message.content.parts" don't (message itself is null), so role/content
    // are simply absent from this row rather than the row being dropped.
    expect(byMessageId['client-created-root']).toEqual({
      conversation_id: 'conv-1',
      title: 'Spaghetti Recipe',
      message_id: 'client-created-root',
    });

    expect('orphan-entry' in byMessageId).toBe(false);

    // conv-2 contributes zero rows (no `mapping` key), but the blueprint
    // as a whole is not aborted -- root item processing continues.
    expect(outcome.extractedData.some(row => row.conversation_id === 'conv-2')).toBe(false);

    // Stats: all 4 mapping entries for conv-1 are counted; the entry
    // missing "message" entirely is caught by the nested required-field
    // check.
    expect(outcome.extractionStats.nNestedRowsTotal).toBe(4);
    expect(outcome.extractionStats.nNestedRowsMissingField).toBe(1);

    // A warning was registered for conv-2's unresolvable nested_loop_path.
    expect(
      outcome.processingErrors.some(e => e.type === 'NESTED_PATH_NOT_FOUND')
    ).toBe(true);
  });

  it('produces identical output to the pre-nested pipeline when nested_loop_path is empty', () => {
    const blueprint = buildNestedBlueprint();
    blueprint.parser_config = { ...(blueprint.parser_config as JSONParserConfig), nested_loop_path: '' };
    // Without nesting, only root-scope fields are matched against each
    // top-level array element's own (flat) keys.
    blueprint.extraction_fields = blueprint.extraction_fields.filter(f => f.scope === 'root');
    blueprint.fields_to_extract = ['conversation_id', 'title'];

    const content = JSON.stringify([
      { conversation_id: 'conv-1', title: 'Spaghetti Recipe' },
      { conversation_id: 'conv-2', title: 'No Mapping Here' },
    ]);

    const outcomeMap = { 1: new BlueprintExtractionOutcome(blueprint) };
    processContent(content, blueprint, outcomeMap);

    const outcome = outcomeMap[1];
    expect(outcome.extractedData).toEqual([
      { conversation_id: 'conv-1', title: 'Spaghetti Recipe' },
      { conversation_id: 'conv-2', title: 'No Mapping Here' },
    ]);
    expect(outcome.extractionStats.nNestedRowsTotal).toBe(0);
    expect(outcome.extractionStats.nNestedRowsMissingField).toBe(0);
  });
});

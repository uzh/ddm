import { describe, it, expect } from 'vitest';
import { applyEntryExclusions } from '@uploader/composables/useDataSubmitter';
import { BlueprintExtractionOutcome } from '@uploader/classes/BlueprintExtractionOutcome';
import { Blueprint } from '@uploader/types/Blueprint';

function buildBlueprint(): Blueprint {
  return {
    id: 1,
    name: 'test',
    description: '',
    format: 'json',
    parser_config: { format: 'json', extraction_root: '', nested_loop_path: 'mapping', array_join_separator: '\n', max_root_entries: null },
    expected_fields: [],
    exp_fields_regex_matching: false,
    nested_expected_fields: [],
    nested_exp_fields_regex_matching: false,
    nested_entry_exclusion_allowed: true,
    nested_display_by_root_item: true,
    fields_to_extract: ['role'],
    extraction_fields: [],
    file_paths: [],
    extraction_rules: [],
    is_backup: false,
    backup_ids: [],
  };
}

describe('applyEntryExclusions', () => {
  it('returns extractedData unchanged when nothing is excluded', () => {
    const outcome = new BlueprintExtractionOutcome(buildBlueprint());
    outcome.extractedData.push({ role: 'user' }, { role: 'assistant' });
    outcome.rowGroupIds.push(0, 0);

    const result = applyEntryExclusions(outcome);

    expect(result).toBe(outcome.extractedData); // same reference, no copy needed
  });

  it('drops every row belonging to an excluded group, keeps the rest', () => {
    const outcome = new BlueprintExtractionOutcome(buildBlueprint());
    // Group 0: two rows (conv-1); Group 1: one row (conv-2).
    outcome.extractedData.push(
      { conversation_id: 'conv-1', role: 'user' },
      { conversation_id: 'conv-1', role: 'assistant' },
      { conversation_id: 'conv-2', role: 'user' },
    );
    outcome.rowGroupIds.push(0, 0, 1);

    outcome.toggleGroupExclusion(0);
    const result = applyEntryExclusions(outcome);

    expect(result).toEqual([{ conversation_id: 'conv-2', role: 'user' }]);
    // The underlying data is untouched -- only the returned (derived) array is filtered.
    expect(outcome.extractedData.length).toBe(3);
  });

  it('restores previously excluded rows once exclusion is toggled back off', () => {
    const outcome = new BlueprintExtractionOutcome(buildBlueprint());
    outcome.extractedData.push({ conversation_id: 'conv-1', role: 'user' });
    outcome.rowGroupIds.push(0);

    outcome.toggleGroupExclusion(0);
    expect(applyEntryExclusions(outcome)).toEqual([]);

    outcome.toggleGroupExclusion(0);
    expect(applyEntryExclusions(outcome)).toEqual([{ conversation_id: 'conv-1', role: 'user' }]);
  });
});

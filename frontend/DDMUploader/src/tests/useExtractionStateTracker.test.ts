import { describe, it, expect } from 'vitest';
import { useExtractionStateTracker } from '@uploader/composables/useExtractionStateTracker';
import { BlueprintExtractionOutcome } from '@uploader/classes/BlueprintExtractionOutcome';
import { ERROR_CATALOG } from '@uploader/utils/errorCatalog';
import { EXTRACTION_STATES } from '@uploader/utils/stateCatalog';
import { JSONParserConfig } from '@uploader/types/ParserConfigs';

const JSONConfig: JSONParserConfig = {
  format: 'json',
  extraction_root: 'items',
  nested_loop_path: '',
  array_join_separator: '\n',
  max_root_entries: null,
}

const blueprint = {
  id: 1,
  name: 'Basic JSON',
  description: 'Tests extraction state',
  format: 'json',
  parser_config: JSONConfig,
  expected_fields: ['name'],
  exp_fields_regex_matching: false,
  nested_expected_fields: [],
  nested_exp_fields_regex_matching: false,
  nested_entry_exclusion_allowed: false,
  nested_display_by_root_item: false,
  fields_to_extract: ['name'],
  extraction_fields: [],
  file_paths: [{ path: 'data.json', is_regex: false }],
  extraction_rules: [],
  is_backup: false,
  backup_ids: [],
};

describe('useExtractionStateTracker', () => {
  it('flips a blueprint to FAILED and surfaces EXTRACTION_ROOT_NOT_FOUND when the extraction root is missing', () => {
    const outcome = new BlueprintExtractionOutcome(blueprint);
    outcome.registerError(ERROR_CATALOG.EXTRACTION_ROOT_NOT_FOUND, { extractionRoot: 'items' });

    const results = { 1: outcome };
    const tracker = useExtractionStateTracker([], results);
    tracker.getExtractionState();

    const blueprintState = tracker.blueprintExtractionStates.value[1];
    expect(blueprintState.state).toBe(EXTRACTION_STATES.FAILED);
    expect(blueprintState.errorsToDisplay).toContainEqual(
      expect.objectContaining({ type: 'EXTRACTION_ROOT_NOT_FOUND' })
    );
  });
});

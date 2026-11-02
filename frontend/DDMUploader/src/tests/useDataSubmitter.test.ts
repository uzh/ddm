import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { ref } from 'vue';
import { applyEntryExclusions, useDataSubmitter } from '@uploader/composables/useDataSubmitter';
import { BlueprintExtractionOutcome } from '@uploader/classes/BlueprintExtractionOutcome';
import { Blueprint } from '@uploader/types/Blueprint';
import { UploaderOutcome } from '@uploader/types/UploaderOutcome';

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

/** A single uploader with one blueprint, consented, with no extracted rows (not relevant to these tests). */
function buildUploaderOutcomes(): Record<number, UploaderOutcome> {
  const outcome = new BlueprintExtractionOutcome(buildBlueprint());
  return {
    1: {
      uploaderName: 'uploader',
      blueprintNames: { 1: 'test' },
      consentMap: { 1: true },
      uploaderState: 'DATA_EXTRACTED',
      blueprintStates: { 1: { state: 'DATA_EXTRACTED', i18nState: '', errorsToDisplay: [] } },
      extractionOutcome: { 1: outcome },
    },
  };
}

describe('useDataSubmitter.submitDonation', () => {
  beforeEach(() => {
    document.body.innerHTML = '<form id="uploader-form"></form>';
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('sets submitFailed and resets submitting on a network error, without throwing', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => { throw new Error('network down'); }));
    const { submitting, submitFailed, submitDonation } = useDataSubmitter(ref(buildUploaderOutcomes()), '/submit');

    const result = await submitDonation();

    expect(result).toBe(false);
    expect(submitting.value).toBe(false);
    expect(submitFailed.value).toBe(true);
  });

  it('sets submitFailed when the response does not redirect (e.g. a rejected submission)', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => ({ redirected: false, status: 400 })));
    const { submitting, submitFailed, submitDonation } = useDataSubmitter(ref(buildUploaderOutcomes()), '/submit');

    const result = await submitDonation();

    expect(result).toBe(false);
    expect(submitting.value).toBe(false);
    expect(submitFailed.value).toBe(true);
  });

  it('resets submitting (not stuck forever) when there is no data to submit', async () => {
    vi.stubGlobal('fetch', vi.fn());
    const { submitting, submitFailed, submitDonation } = useDataSubmitter(ref({}), '/submit');

    const result = await submitDonation();

    expect(result).toBe(false);
    expect(submitting.value).toBe(false);
    expect(submitFailed.value).toBe(true);
    expect(fetch).not.toHaveBeenCalled();
  });

  it('resets submitFailed on a new attempt after a prior failure', async () => {
    let callCount = 0;
    vi.stubGlobal('fetch', vi.fn(async () => {
      callCount++;
      if (callCount === 1) throw new Error('network down');
      return { redirected: true, url: '/debriefing' };
    }));
    // jsdom doesn't implement real navigation; stub window.location so the
    // success path's `window.location.href = ...` doesn't log a jsdom
    // "Not implemented: navigation" error for this test.
    const originalLocation = window.location;
    Object.defineProperty(window, 'location', { writable: true, value: { href: '' } });

    const { submitFailed, submitDonation } = useDataSubmitter(ref(buildUploaderOutcomes()), '/submit');

    await submitDonation();
    expect(submitFailed.value).toBe(true);

    await submitDonation();
    expect(submitFailed.value).toBe(false);

    Object.defineProperty(window, 'location', { writable: true, value: originalLocation });
  });
});

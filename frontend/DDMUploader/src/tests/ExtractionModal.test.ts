import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';
import ExtractionModal from '@uploader/components/ExtractionModal.vue';
import { BlueprintExtractionOutcome } from '@uploader/classes/BlueprintExtractionOutcome';
import { Blueprint } from '@uploader/types/Blueprint';
import { ExtractionFieldLayout } from '@uploader/types/ExtractionFieldLayout';
import { groupEntriesByRowGroupId } from '@uploader/utils/entryGroup';
import en from '@uploader/locales/en.json';

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en },
});

function buildBlueprint(groupByRootItem: boolean, allowDeletion: boolean = false): Blueprint {
  return {
    id: 1,
    name: 'ChatGPT export',
    description: '',
    format: 'json',
    parser_config: {
      format: 'json',
      extraction_root: '',
      nested_loop_path: 'mapping',
      array_join_separator: '\n',
      max_root_entries: null,
    },
    expected_fields: ['conversation_id'],
    exp_fields_regex_matching: false,
    nested_expected_fields: [],
    nested_exp_fields_regex_matching: false,
    nested_display_by_root_item: groupByRootItem,
    nested_entry_exclusion_allowed: allowDeletion,
    fields_to_extract: ['conversation_id', 'title', 'role', 'content'],
    extraction_fields: [
      { id: 1, scope: 'root', expected_name: 'conversation_id', match_regex: false, keep_in_donation: true, alias: null },
      { id: 2, scope: 'root', expected_name: 'title', match_regex: false, keep_in_donation: true, alias: null },
      { id: 3, scope: 'nested', expected_name: 'message.author.role', match_regex: false, keep_in_donation: true, alias: 'role' },
      { id: 4, scope: 'nested', expected_name: 'message.content.parts', match_regex: false, keep_in_donation: true, alias: 'content' },
    ],
    file_paths: [],
    extraction_rules: [],
    is_backup: false,
    backup_ids: [],
  };
}

/** Simulates what processContent() would have populated, without running the full engine. */
function buildOutcome(blueprint: Blueprint): BlueprintExtractionOutcome {
  const outcome = new BlueprintExtractionOutcome(blueprint);

  outcome.extractedFieldsMap.set('conversation_id', 'conversation_id');
  outcome.extractedFieldsMap.set('title', 'title');
  outcome.extractedFieldsMap.set('role', 'message.author.role');
  outcome.extractedFieldsMap.set('content', 'message.content.parts');

  const groupA = outcome.nextGroupId();
  const groupB = outcome.nextGroupId();

  const rows: [number, Record<string, any>][] = [
    [groupA, { conversation_id: 'conv-1', title: 'Spaghetti Recipe', role: 'user', content: 'Spaghetti' }],
    [groupA, { conversation_id: 'conv-1', title: 'Spaghetti Recipe', role: 'assistant', content: 'Line1\nLine2' }],
    [groupB, { conversation_id: 'conv-2', title: 'Other Chat', role: 'user', content: 'Hello' }],
  ];
  for (const [groupId, row] of rows) {
    outcome.extractedData.push(row);
    outcome.rowGroupIds.push(groupId);
  }

  return outcome;
}

/**
 * Same shape as buildOutcome, but with a third entry inserted between two
 * matching entries, so tests can prove that navigation skips over it rather
 * than just landing on "the next index".
 */
function buildOutcomeWithNonMatchingMiddleEntry(blueprint: Blueprint): BlueprintExtractionOutcome {
  const outcome = new BlueprintExtractionOutcome(blueprint);

  outcome.extractedFieldsMap.set('conversation_id', 'conversation_id');
  outcome.extractedFieldsMap.set('title', 'title');
  outcome.extractedFieldsMap.set('role', 'message.author.role');
  outcome.extractedFieldsMap.set('content', 'message.content.parts');

  const groupA = outcome.nextGroupId();
  const groupB = outcome.nextGroupId();
  const groupC = outcome.nextGroupId();

  const rows: [number, Record<string, any>][] = [
    [groupA, { conversation_id: 'conv-1', title: 'First', role: 'user', content: 'target' }],
    [groupB, { conversation_id: 'conv-2', title: 'Second', role: 'user', content: 'Hello' }],
    [groupC, { conversation_id: 'conv-3', title: 'Third', role: 'user', content: 'target' }],
  ];
  for (const [groupId, row] of rows) {
    outcome.extractedData.push(row);
    outcome.rowGroupIds.push(groupId);
  }

  return outcome;
}

/** Mirrors the fieldLayout ExtractionItem.vue computes for its ExtractionPreview/ExtractionModal children. */
function buildFieldLayout(blueprint: Blueprint, outcome: BlueprintExtractionOutcome): ExtractionFieldLayout {
  const parserConfig = blueprint.parser_config as { nested_loop_path?: string };
  const isGrouped = !!(blueprint.nested_display_by_root_item && parserConfig?.nested_loop_path);

  const nestedFieldNames = new Set(
    blueprint.extraction_fields.filter(f => f.scope === 'nested').map(f => f.alias || f.expected_name)
  );
  const allKeys = Array.from(outcome.extractedFieldsMap.keys());
  const nestedFieldKeys = allKeys.filter(key => nestedFieldNames.has(key));
  const rootFieldKeys = allKeys.filter(key => !nestedFieldNames.has(key));

  const nestedColumns = new Map<string, string>();
  for (const key of nestedFieldKeys) {
    const label = outcome.extractedFieldsMap.get(key);
    if (label !== undefined) nestedColumns.set(key, label);
  }

  return {
    isGrouped,
    groups: groupEntriesByRowGroupId(outcome),
    rootFieldKeys,
    nestedColumns,
  };
}

describe('ExtractionModal', () => {
  it('renders one table per root item, with a root-value summary line, when group_by_root_item is on', () => {
    const blueprint = buildBlueprint(true);
    const blueprintOutcome = buildOutcome(blueprint);
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionModal, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
    });

    const summary = wrapper.find('.group-root-summary');
    expect(summary.exists()).toBe(true);
    expect(summary.text()).toContain('conversation_id: conv-1');
    expect(summary.text()).toContain('title: Spaghetti Recipe');

    // Only the two nested-scope columns appear as table headers -- not
    // conversation_id/title, which are shown in the summary line instead.
    const headers = wrapper.find('.review-table thead').findAll('th').map(th => th.text());
    expect(headers).toEqual(['message.author.role', 'message.content.parts']);

    // Only conv-1's rows (the first group) appear in the table.
    expect(wrapper.find('.review-table tbody').text()).not.toContain('conv-2');
  });

  it('navigates between entries without mixing up their rows', async () => {
    const blueprint = buildBlueprint(true);
    const blueprintOutcome = buildOutcome(blueprint);
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionModal, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
      attachTo: document.body,
    });

    expect(wrapper.text()).toContain('Entry 1 of 2');

    const nextButton = wrapper.find('[aria-label="Next entry"]');
    await nextButton.trigger('click');

    expect(wrapper.text()).toContain('Entry 2 of 2');
    expect(wrapper.text()).toContain('conv-2');
    expect(wrapper.text()).not.toContain('Spaghetti Recipe');

    wrapper.unmount();
  });

  it('does not show a delete control when allow_nested_entry_deletion is off', () => {
    const blueprint = buildBlueprint(true, false);
    const blueprintOutcome = buildOutcome(blueprint);
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionModal, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
    });

    expect(wrapper.find('.entry-deletion-control').exists()).toBe(false);
  });

  it('toggles entry exclusion reversibly, without touching extractedData', async () => {
    const blueprint = buildBlueprint(true, true);
    const blueprintOutcome = buildOutcome(blueprint);
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);
    const originalLength = blueprintOutcome.extractedData.length;

    const wrapper = mount(ExtractionModal, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
      attachTo: document.body,
    });

    const removeButton = wrapper.find('.entry-deletion-control button');
    expect(removeButton.text()).toBe('Remove this element from my donation');
    expect(blueprintOutcome.excludedGroupIds.size).toBe(0);

    await removeButton.trigger('click');

    // The group id (conv-1's) is now marked excluded, but the underlying
    // extractedData/rowGroupIds arrays are completely untouched -- the
    // actual filtering only happens at submission time.
    expect(blueprintOutcome.excludedGroupIds.has(0)).toBe(true);
    expect(blueprintOutcome.extractedData.length).toBe(originalLength);
    expect(wrapper.text()).toContain('This element will not be included in your donation.');
    expect(wrapper.find('.entry-deletion-control button').text()).toBe('Keep this element in my donation');

    // Toggling again restores it.
    await wrapper.find('.entry-deletion-control button').trigger('click');
    expect(blueprintOutcome.excludedGroupIds.has(0)).toBe(false);
    expect(wrapper.text()).not.toContain('This entry will not be included in your donation.');

    wrapper.unmount();
  });

  it('cross-element search jumps to the entry containing the match', async () => {
    const blueprint = buildBlueprint(true);
    const blueprintOutcome = buildOutcome(blueprint);
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionModal, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
      attachTo: document.body,
    });

    expect(wrapper.text()).toContain('Entry 1 of 2');

    // "Hello" only appears in conv-2's content, the second entry. While
    // filtered, the nav label reports position among matches (1 of 1),
    // not the entry's position among all groups.
    const searchInput = wrapper.find('[aria-label="Search entries across all elements"]');
    await searchInput.setValue('Hello');
    await new Promise(resolve => setTimeout(resolve, 350));

    expect(wrapper.text()).toContain('Entry 1 of 1');
    expect(wrapper.text()).toContain('conv-2');
    expect(wrapper.text()).toContain('The term was found in 1 of 2 elements');

    wrapper.unmount();
  });

  it('cross-element search reports a count when multiple entries match', async () => {
    const blueprint = buildBlueprint(true);
    const blueprintOutcome = buildOutcome(blueprint);
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionModal, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
      attachTo: document.body,
    });

    // Both conv-1 (row 1) and conv-2 have a row with role "user".
    const searchInput = wrapper.find('[aria-label="Search entries across all elements"]');
    await searchInput.setValue('user');
    await new Promise(resolve => setTimeout(resolve, 350));

    expect(wrapper.text()).toContain('The term was found in 2 of 2 elements');

    wrapper.unmount();
  });

  it('cross-element search shows a not-found message and hides entry navigation when nothing matches', async () => {
    const blueprint = buildBlueprint(true);
    const blueprintOutcome = buildOutcome(blueprint);
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionModal, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
      attachTo: document.body,
    });

    const searchInput = wrapper.find('[aria-label="Search entries across all elements"]');
    await searchInput.setValue('no-such-term-anywhere');
    await new Promise(resolve => setTimeout(resolve, 350));

    expect(wrapper.text()).toContain('No entries found');
    expect(wrapper.text()).not.toContain('Entry 1 of 2');

    wrapper.unmount();
  });

  it('while a cross-element search is active, Next/Previous entry skip non-matching entries', async () => {
    const blueprint = buildBlueprint(true);
    const blueprintOutcome = buildOutcomeWithNonMatchingMiddleEntry(blueprint);
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionModal, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
      attachTo: document.body,
    });

    // "target" matches conv-1 and conv-3, but not conv-2 in between.
    const searchInput = wrapper.find('[aria-label="Search entries across all elements"]');
    await searchInput.setValue('target');
    await new Promise(resolve => setTimeout(resolve, 350));

    expect(wrapper.text()).toContain('conv-1');

    const nextButton = wrapper.find('[aria-label="Next entry"]');
    await nextButton.trigger('click');

    // conv-2 was skipped entirely -- landed straight on conv-3.
    expect(wrapper.text()).toContain('conv-3');
    expect(wrapper.text()).not.toContain('conv-2');

    // Already on the last match: Next is disabled.
    expect(wrapper.find('[aria-label="Next entry"]').attributes('disabled')).toBeDefined();

    const prevButton = wrapper.find('[aria-label="Previous entry"]');
    await prevButton.trigger('click');

    // Stepping back also skips conv-2 and returns straight to conv-1.
    expect(wrapper.text()).toContain('conv-1');
    expect(wrapper.text()).not.toContain('conv-2');
    expect(wrapper.find('[aria-label="Previous entry"]').attributes('disabled')).toBeDefined();

    wrapper.unmount();
  });

  it('clearing the search restores normal one-by-one navigation through all entries', async () => {
    const blueprint = buildBlueprint(true);
    const blueprintOutcome = buildOutcomeWithNonMatchingMiddleEntry(blueprint);
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionModal, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
      attachTo: document.body,
    });

    const searchInput = wrapper.find('[aria-label="Search entries across all elements"]');
    await searchInput.setValue('target');
    await new Promise(resolve => setTimeout(resolve, 350));
    expect(wrapper.text()).toContain('conv-1');

    await searchInput.setValue('');
    await new Promise(resolve => setTimeout(resolve, 350));

    const nextButton = wrapper.find('[aria-label="Next entry"]');
    await nextButton.trigger('click');

    // With no active search, Next steps to the very next entry, conv-2.
    expect(wrapper.text()).toContain('conv-2');

    wrapper.unmount();
  });

  it('does not show entry navigation or the cross-element search when there is only one entry', () => {
    const blueprint = buildBlueprint(true);
    const blueprintOutcome = buildOutcome(blueprint);
    // Collapse to a single group by removing conv-2's row.
    blueprintOutcome.extractedData.pop();
    blueprintOutcome.rowGroupIds.pop();
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionModal, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
    });

    expect(wrapper.find('[aria-label="Next entry"]').exists()).toBe(false);
    expect(wrapper.find('[aria-label="Search entries across all elements"]').exists()).toBe(false);
  });

  it('renders the flat single-table view, with pagination and search, when group_by_root_item is off', async () => {
    const blueprint = buildBlueprint(false);
    const blueprintOutcome = buildOutcome(blueprint);
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionModal, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
      attachTo: document.body,
    });

    expect(wrapper.find('.group-root-summary').exists()).toBe(false);
    const rows = wrapper.find('.review-table tbody').findAll('tr');
    expect(rows.length).toBe(3);

    const searchInput = wrapper.find('[aria-label="Search data entries"]');
    await searchInput.setValue('conv-2');
    await new Promise(resolve => setTimeout(resolve, 350));

    expect(wrapper.find('.review-table tbody').findAll('tr').length).toBe(1);
    expect(wrapper.find('.review-table tbody').text()).toContain('conv-2');

    wrapper.unmount();
  });
});

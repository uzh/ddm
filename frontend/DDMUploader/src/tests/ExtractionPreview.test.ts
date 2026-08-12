import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';
import ExtractionPreview from '@uploader/components/ExtractionPreview.vue';
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

function buildBlueprint(groupByRootItem: boolean): Blueprint {
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
    nested_entry_exclusion_allowed: false,
    nested_display_by_root_item: groupByRootItem,
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

describe('ExtractionPreview', () => {
  it('renders the flat single-table view when group_by_root_item is off', () => {
    const blueprint = buildBlueprint(false);
    const blueprintOutcome = buildOutcome(blueprint);
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionPreview, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
    });

    const previewRows = wrapper.find('.preview-table tbody').findAll('tr');
    expect(previewRows.length).toBe(3);
    expect(wrapper.find('.group-root-summary').exists()).toBe(false);
    expect(wrapper.text()).toContain('conv-1');
  });

  it('shows only the first group’s rows, under its root-value summary, when group_by_root_item is on', () => {
    const blueprint = buildBlueprint(true);
    const blueprintOutcome = buildOutcome(blueprint);
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionPreview, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
    });

    const summary = wrapper.find('.group-root-summary');
    expect(summary.exists()).toBe(true);
    expect(summary.text()).toContain('conversation_id: conv-1');
    expect(summary.text()).toContain('title: Spaghetti Recipe');

    // Only the two nested-scope columns appear as table headers -- not
    // conversation_id/title, which are shown in the summary line instead.
    const headers = wrapper.find('.preview-table thead').findAll('th').map(th => th.text());
    expect(headers).toEqual(['message.author.role', 'message.content.parts']);

    // Only the first group's (conv-1's) rows appear -- conv-2's row is a
    // separate entry and must not leak into this group's preview table.
    const previewRows = wrapper.find('.preview-table tbody').findAll('tr');
    expect(previewRows.length).toBe(2);
    expect(wrapper.find('.preview-table tbody').text()).not.toContain('Hello');
  });

  it('shows a "show complete list" link with the remaining count when there are more than 3 entries', () => {
    const blueprint = buildBlueprint(false);
    const blueprintOutcome = buildOutcome(blueprint);
    blueprintOutcome.extractedData.push({ conversation_id: 'conv-3', title: 'Third', role: 'user', content: 'Hi' });
    blueprintOutcome.rowGroupIds.push(blueprintOutcome.nextGroupId());
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionPreview, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
    });

    expect(wrapper.text()).toContain('1 more entries');
    const link = wrapper.find('[data-bs-target="#reviewModal1"]');
    expect(link.exists()).toBe(true);
    expect(link.text()).toBe('show complete list');
  });

  it('does not show the "show complete list" link when there are 3 or fewer entries', () => {
    const blueprint = buildBlueprint(false);
    const blueprintOutcome = buildOutcome(blueprint);
    const fieldLayout = buildFieldLayout(blueprint, blueprintOutcome);

    const wrapper = mount(ExtractionPreview, {
      global: { plugins: [i18n] },
      props: { blueprint, blueprintOutcome, fieldLayout },
    });

    expect(wrapper.find('[data-bs-target="#reviewModal1"]').exists()).toBe(false);
  });
});

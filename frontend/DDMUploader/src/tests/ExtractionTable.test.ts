import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import ExtractionTable from '@uploader/components/ExtractionTable.vue';

describe('ExtractionTable', () => {
  const columns = new Map([
    ['conversation_id', 'conversation_id'],
    ['title', 'title'],
  ]);

  it('renders one header per column, using the label', () => {
    const wrapper = mount(ExtractionTable, {
      props: { columns, rows: [] },
    });

    const headers = wrapper.findAll('thead th').map(th => th.text());
    expect(headers).toEqual(['conversation_id', 'title']);
  });

  it('renders one row per item, with cells in column order', () => {
    const rows = [
      { conversation_id: 'conv-1', title: 'Spaghetti Recipe' },
      { conversation_id: 'conv-2', title: 'Other Chat' },
    ];

    const wrapper = mount(ExtractionTable, {
      props: { columns, rows },
    });

    const bodyRows = wrapper.findAll('tbody tr');
    expect(bodyRows.length).toBe(2);
    expect(bodyRows[0].findAll('td').map(td => td.text())).toEqual(['conv-1', 'Spaghetti Recipe']);
    expect(bodyRows[1].findAll('td').map(td => td.text())).toEqual(['conv-2', 'Other Chat']);
  });

  it('renders a dash for a column missing from a given row', () => {
    const rows = [{ conversation_id: 'conv-1' }];

    const wrapper = mount(ExtractionTable, {
      props: { columns, rows },
    });

    expect(wrapper.findAll('tbody td').map(td => td.text())).toEqual(['conv-1', '–']);
  });

  it('shows the empty message in a single row when there is no data', () => {
    const wrapper = mount(ExtractionTable, {
      props: { columns, rows: [], emptyMessage: 'No entries found' },
    });

    const bodyRows = wrapper.findAll('tbody tr');
    expect(bodyRows.length).toBe(1);
    expect(bodyRows[0].text()).toBe('No entries found');
  });

  it('applies the tableClass prop to the table element', () => {
    const wrapper = mount(ExtractionTable, {
      props: { columns, rows: [], tableClass: 'preview-table' },
    });

    expect(wrapper.find('table').classes()).toContain('preview-table');
  });
});

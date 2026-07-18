import { describe, it, vi, expect, beforeEach } from 'vitest';
import { useFileProcessor } from '@uploader/composables/useFileProcessor';
import JSZip from 'jszip';
import {ERROR_CATALOG} from "@uploader/utils/errorCatalog";
import { regexDeleteMatch, valueIsEqual } from "@uploader/utils/ExtractionFunctions";
import { extractData, getFieldKeyMap } from '@uploader/composables/useFileProcessor/extractionEngine';
import {ExtractionRule} from "@uploader/types/ExtractionRule";

// Blueprint stub for JSON
const jsonBlueprint = {
  id: 1,
  name: 'Basic JSON',
  description: 'Tests simple JSON processing',
  format: 'json',
  json_extraction_root: '',
  expected_fields: ['name'],
  exp_fields_regex_matching: false,
  fields_to_extract: ['name'],
  extraction_fields: [
    {
      id: 1,
      expected_name: 'name',
      match_regex: false,
      keep_in_donation: true,
      alias: '',
    }
  ],
  file_paths: [
    {
      path: '.*\\.json',
      is_regex: true
    }
  ],
  csv_delimiter: ',',
  extraction_rules: [
    {
      id: 1,
      field: 'name',
      comparison_operator: null,
      comparison_value: null,
      replacement_value: null
    }
  ]
};

// Blueprint stub for CSV
const csvBlueprint = {
  ...jsonBlueprint,
  id: 2,
  format: 'csv',
  expected_fields: ['name'],
  csv_delimiter: ',',
  file_paths: [
    {
      path: '.*\\.csv',
      is_regex: true
    }
  ],
};

// Dummy JSON file
const jsonData = JSON.stringify([{ name: 'Alice' }, { name: 'Bob' }]);
const jsonFile = new File([jsonData], 'test.json', { type: 'application/json' });

// Dummy CSV file
const csvData = 'name\nAlice\nBob';
const csvFile = new File([csvData], 'test.csv', { type: 'text/csv' });

// Helper: Create ZIP containing a JSON file
async function createZipFile(): Promise<File> {
  const zip = new JSZip();
  zip.file('data.json', jsonData);
  const blob = await zip.generateAsync({ type: 'blob' });
  return new File([blob], 'test.zip', { type: 'application/zip' });
}

describe('useFileProcessor', () => {
  it('initializes with empty state and prepares result maps', async () => {
    const processor = useFileProcessor(false, [jsonBlueprint]);
    expect(processor.generalErrors).toEqual([]);
    expect(Object.keys(processor.blueprintOutcomeMap)).toContain('1');
  });

  it('processes a simple JSON file correctly', async () => {
    const processor = useFileProcessor(false, [jsonBlueprint]);
    await processor.handleSelectedFile(jsonFile);

    const result = processor.blueprintOutcomeMap[1];
    expect(result.extractedData.length).toBe(2);
    expect(result.extractedData[0]).toHaveProperty('name', 'Alice');
    expect(result.extractionStats.nRowsTotal).toBe(2);
  });

  it('processes a CSV file correctly', async () => {
    const processor = useFileProcessor(false, [csvBlueprint]);
    await processor.handleSelectedFile(csvFile);

    const result = processor.blueprintOutcomeMap[2];
    expect(result.extractedData.length).toBe(2);
    expect(result.extractedData[1]).toHaveProperty('name', 'Bob');
  });

  it('processes a ZIP file and matches blueprint file', async () => {
    const zipFile = await createZipFile();
    const processor = useFileProcessor(true, [jsonBlueprint]);
    await processor.handleSelectedFile(zipFile);

    const result = processor.blueprintOutcomeMap[1];
    expect(result.extractedData.length).toBe(2);
    expect(result.extractedData[0].name).toBe('Alice');
  });

  it('handles unsupported file type gracefully', async () => {
    const badFile = new File(['<html></html>'], 'fake.html', { type: 'text/html' });
    const processor = useFileProcessor(false, [jsonBlueprint]);
    await processor.handleSelectedFile(badFile);

    expect(processor.blueprintOutcomeMap[1].processingErrors.length).toBeGreaterThan(0);
    expect(processor.blueprintOutcomeMap[1].extractedData).toEqual([]);
  });

  it('handles invalid ZIP gracefully', async () => {
    const badZip = new File(['notzip'], 'fake.zip', { type: 'application/zip' });
    const processor = useFileProcessor(true, [jsonBlueprint]);
    await processor.handleSelectedFile(badZip);

    expect(processor.generalErrors.length).toBeGreaterThan(0);
  });

  it('registers blueprint errors for unmatched regex', async () => {
    const zip = new JSZip();
    zip.file('unmatched.json', jsonData); // will not match the pattern
    const blob = await zip.generateAsync({ type: 'blob' });
    const zipFile = new File([blob], 'unmatched.zip', { type: 'application/zip' });

    const badRegexBlueprint = {
      ...jsonBlueprint,
      file_paths: [
        {
          path: '^no-match\\.json$',
          is_regex: true
        }
      ],
    };
    const processor = useFileProcessor(true, [badRegexBlueprint]);
    await processor.handleSelectedFile(zipFile);

    expect(processor.generalErrors.length).toBe(0);
    expect(processor.blueprintOutcomeMap[1].extractedData).toEqual([]);
    expect(processor.blueprintOutcomeMap[1].processingErrors.length).toBeGreaterThan(0);
  });
});


function createMockOutcome() {
  return {
    registerError: vi.fn(),
    mapExtractedKey: vi.fn(),
    registerNoKeyMatch: vi.fn(),
  };
}

describe('getFieldKeyMap', () => {
  let outcome;
  let blueprintOutcomeMap;

  beforeEach(() => {
    outcome = createMockOutcome();
    blueprintOutcomeMap = { 1: outcome };
  });

  it('maps a field to its exact matching key', () => {
    const dataRow = { name: 'Alice', number: 1 };
    const extractionFields = [
      { id: 1, expected_name: 'name', match_regex: false, keep_in_donation: true, alias: null },
    ];

    const result = getFieldKeyMap(dataRow, extractionFields, 1, blueprintOutcomeMap);

    expect(result.get('name')).toBe('name');
    expect(outcome.mapExtractedKey).toHaveBeenCalledWith('name', 'name');
    expect(outcome.registerError).not.toHaveBeenCalled();
    expect(outcome.registerNoKeyMatch).not.toHaveBeenCalled();
  });

  it('uses alias as the resulting map key when provided', () => {
    const dataRow = { raw_name: 'Alice' };
    const extractionFields = [
      { id: 1, expected_name: 'raw_name', match_regex: false, keep_in_donation: true, alias: 'clean_name' },
    ];

    const result = getFieldKeyMap(dataRow, extractionFields, 1, blueprintOutcomeMap);

    expect(result.get('clean_name')).toBe('raw_name');
    expect(result.has('raw_name')).toBe(false);
  });

  it('matches keys via regex when match_regex is true', () => {
    const dataRow = { item_1: 'a', other: 'x' };
    const extractionFields = [
      { id: 1, expected_name: '^item_1$', match_regex: true, keep_in_donation: true, alias: null },
    ];

    const result = getFieldKeyMap(dataRow, extractionFields, 1, blueprintOutcomeMap);

    expect(result.get('^item_1$')).toBe('item_1');
  });

  it('registers no-key-match when nothing in the row matches', () => {
    const dataRow = { unrelated: 'x' };
    const extractionFields = [
      { id: 1, expected_name: 'missing_field', match_regex: false, keep_in_donation: true, alias: null },
    ];

    const result = getFieldKeyMap(dataRow, extractionFields, 1, blueprintOutcomeMap);

    expect(result.has('missing_field')).toBe(false);
    expect(outcome.registerNoKeyMatch).toHaveBeenCalledWith('missing_field', Object.keys(dataRow));
  });

  it('registers an error and falls back to the first match when a regex matches multiple keys', () => {
    const dataRow = { item_1: 'a', item_2: 'b' };
    const extractionFields = [
      { id: 1, expected_name: '^item_\\d+$', match_regex: true, keep_in_donation: true, alias: null },
    ];

    const result = getFieldKeyMap(dataRow, extractionFields, 1, blueprintOutcomeMap);

    expect(result.get('^item_\\d+$')).toBe('item_1');
    expect(outcome.registerError).toHaveBeenCalledWith(
      ERROR_CATALOG.MORE_THAN_ONE_KEY_MATCH,
      expect.objectContaining({ field: '^item_\\d+$', keys: ['item_1', 'item_2'], defaultKey: 'item_1' })
    );
  });

  it('registers an error and skips the field when the regex pattern is invalid', () => {
    const dataRow = { name: 'Alice' };
    const extractionFields = [
      { id: 1, expected_name: '(unclosed', match_regex: true, keep_in_donation: true, alias: null },
    ];

    const result = getFieldKeyMap(dataRow, extractionFields, 1, blueprintOutcomeMap);

    expect(result.has('(unclosed')).toBe(false);
    expect(outcome.registerError).toHaveBeenCalledWith(
      ERROR_CATALOG.INVALID_FIELD_REGEX,
      { blueprintId: 1, fieldExpectedName: '(unclosed' }
    );
  });

  it('keeps the first match when two fields resolve to the same output key', () => {
    const dataRow = { name: 'Alice', alt_name: 'Bob' };
    const extractionFields = [
      { id: 1, expected_name: 'name', match_regex: false, keep_in_donation: true, alias: 'display_name' },
      { id: 2, expected_name: 'alt_name', match_regex: false, keep_in_donation: true, alias: 'display_name' },
    ];

    const result = getFieldKeyMap(dataRow, extractionFields, 1, blueprintOutcomeMap);

    expect(result.get('display_name')).toBe('name');
    expect(result.size).toBe(1);
  });

  it('returns an empty map when there are no extraction fields', () => {
    const result = getFieldKeyMap({ name: 'Alice' }, [], 1, blueprintOutcomeMap);
    expect(result.size).toBe(0);
  });
});

vi.mock('@uploader/utils/ExtractionFunctions', () => ({
  valueIsEqual: vi.fn(),
  valueIsNotEqual: vi.fn(),
  valueIsSmaller: vi.fn(),
  valueIsGreater: vi.fn(),
  valueIsSmallerOrEqual: vi.fn(),
  valueIsGreaterOrEqual: vi.fn(),
  regexDeleteMatch: vi.fn((value: string) => value),
  regexReplaceMatch: vi.fn((value: string) => value),
  regexDeleteRow: vi.fn(() => false),
}));

function createMockOutcomeExtractData() {
  return {
    extractedData: [] as Record<string, any>[],
    extractionRuleLog: {} as Record<number, number>,
    incrementExtractionRuleCount: vi.fn(),
  };
}

describe('extractData', () => {
  let outcome: ReturnType<typeof createMockOutcomeExtractData>;
  let blueprintOutcomeMap: Record<number, any>;

  beforeEach(() => {
    vi.clearAllMocks();
    outcome = createMockOutcomeExtractData();
    blueprintOutcomeMap = { 1: outcome };
  });

  it('extracts and pushes fields present in fieldsToExtract', () => {
    const dataRow = { name: 'Alice', age: '30' };
    const fieldKeyMap = new Map([['name', 'name']]);

    extractData(dataRow, ['name'], [], fieldKeyMap, 1, blueprintOutcomeMap);

    expect(outcome.extractedData).toEqual([{ name: 'Alice' }]);
  });

  it('does not push when no fields in fieldKeyMap are in fieldsToExtract', () => {
    const dataRow = { name: 'Alice' };
    const fieldKeyMap = new Map([['name', 'name']]);

    extractData(dataRow, ['other_field'], [], fieldKeyMap, 1, blueprintOutcomeMap);

    expect(outcome.extractedData).toEqual([]);
  });

  it('skips a rule when its field has no entry in fieldKeyMap', () => {
    const dataRow = { name: 'Alice' };
    const fieldKeyMap = new Map<string, string>(); // empty — 'name' not mapped
    const rules = [
      { id: 1, field: 'name', comparison_operator: '==', comparison_value: 'Alice' },
    ] as ExtractionRule[];

    expect(() =>
      extractData(dataRow, ['name'], rules, fieldKeyMap, 1, blueprintOutcomeMap)
    ).not.toThrow();
    expect(valueIsEqual).not.toHaveBeenCalled();
  });

  it('discards the row when a comparison operator matches', () => {
    (valueIsEqual as any).mockReturnValue(true);

    const dataRow = { name: 'Alice' };
    const fieldKeyMap = new Map([['name', 'name']]);
    const rules = [
      { id: 1, field: 'name', comparison_operator: '==', comparison_value: 'Alice' },
    ] as ExtractionRule[];

    extractData(dataRow, ['name'], rules, fieldKeyMap, 1, blueprintOutcomeMap);
    expect(outcome.extractedData).toEqual([]);
  });

  it('keeps the row when a comparison operator does not match', () => {
    (valueIsEqual as any).mockReturnValue(false);

    const dataRow = { name: 'Alice' };
    const fieldKeyMap = new Map([['name', 'name']]);
    const rules = [
      { id: 1, field: 'name', comparison_operator: '==', comparison_value: 'Bob' },
    ] as ExtractionRule[];

    extractData(dataRow, ['name'], rules, fieldKeyMap, 1, blueprintOutcomeMap);

    expect(outcome.extractedData).toEqual([{ name: 'Alice' }]);
  });

  it('applies a regex-delete-match transform and logs rule usage', () => {
    (regexDeleteMatch as any).mockReturnValue('cleaned');
    outcome.extractionRuleLog[1] = 0;

    const dataRow = { name: 'raw-value' };
    const fieldKeyMap = new Map([['name', 'name']]);
    const rules = [
      { id: 1, field: 'name', comparison_operator: 'regex-delete-match', comparison_value: '-.*' },
    ] as ExtractionRule[];

    extractData(dataRow, ['name'], rules, fieldKeyMap, 1, blueprintOutcomeMap);

    expect(dataRow.name).toBe('cleaned');
    expect(outcome.extractionRuleLog[1]).toBe(1);
    expect(outcome.extractedData).toEqual([{ name: 'cleaned' }]);
  });

  it('does not throw and does not log rule usage when a transform throws', () => {
    (regexDeleteMatch as any).mockImplementation(() => {
      throw new Error('bad regex');
    });
    outcome.extractionRuleLog[1] = 0;

    const dataRow = { name: 'raw-value' };
    const fieldKeyMap = new Map([['name', 'name']]);
    const rules = [
      { id: 1, field: 'name', comparison_operator: 'regex-delete-match', comparison_value: '(bad' },
    ] as ExtractionRule[];

    expect(() =>
      extractData(dataRow, ['name'], rules, fieldKeyMap, 1, blueprintOutcomeMap)
    ).not.toThrow();
    expect(outcome.extractionRuleLog[1]).toBe(0);
  });
});

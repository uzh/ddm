import { describe, it, expect, beforeEach } from 'vitest';
import { useFileProcessor } from '@uploader/composables/useFileProcessor';
import JSZip from 'jszip';

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
  regex_path: '.*\\.json',
  csv_delimiter: ',',
  extraction_rules: [
    {
      id: 1,
      field: 'name',
      regex_field: false,
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
  regex_path: '.*\\.csv'
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

    const badRegexBlueprint = { ...jsonBlueprint, regex_path: '^no-match\\.json$' };
    const processor = useFileProcessor(true, [badRegexBlueprint]);
    await processor.handleSelectedFile(zipFile);

    expect(processor.generalErrors.length).toBe(0);
    expect(processor.blueprintOutcomeMap[1].extractedData).toEqual([]);
    expect(processor.blueprintOutcomeMap[1].processingErrors.length).toBeGreaterThan(0);
  });
});

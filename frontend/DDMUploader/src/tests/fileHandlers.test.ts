import { describe, it, expect } from 'vitest';
import { handleZipFile, handleSingleFile, fileIsZip } from '@uploader/composables/useFileProcessor/fileHandlers';
import { BlueprintExtractionOutcome } from '@uploader/classes/BlueprintExtractionOutcome';
import JSZip from 'jszip';

// Blueprint stubs for JSON
const jsonBlueprintA = {
  id: 1,
  name: 'Basic JSON',
  description: 'Tests simple JSON processing',
  format: 'json',
  json_extraction_root: '',
  expected_fields: ['name'],
  exp_fields_regex_matching: false,
  fields_to_extract: ['name'],
  regex_path: 'data_a.json',
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

const jsonBlueprintBoth = {
  ...jsonBlueprintA,
  id: 2,
  name: 'Basic JSON',
  description: 'Tests simple JSON processing',
  regex_path: 'data.*\\.json',
};

// CSV Blueprint
const csvBlueprint = {
  ...jsonBlueprintA,
  id: 3,
  format: 'csv',
  regex_path: '.*\\.csv',
  csv_delimiter: ','
};

// Dummy JSON data
const jsonDataA = JSON.stringify([{ name: 'Alice' }, { name: 'Bob' }]);
const jsonDataB = JSON.stringify([{ name: 'Chester' }, { name: 'Diana' }]);

// Dummy CSV data
const csvData = 'name\nAlice\nBob';

// Helper: Create ZIP containing JSON files
async function createZipFile(): Promise<File> {
  const zip = new JSZip();
  zip.file('data_a.json', jsonDataA);
  zip.file('data_b.json', jsonDataB);
  const blob = await zip.generateAsync({ type: 'blob' });
  return new File([blob], 'test.zip', { type: 'application/zip' });
}

describe('fileIsZip', () => {
  it('validates files with correct extension and MIME type', () => {
    const validZip = new File(['content'], 'test.zip', { type: 'application/zip' });
    expect(fileIsZip(validZip)).toBe(true);
  });

  it('accepts alternative ZIP MIME types', () => {
    const zipCompressed = new File(['content'], 'test.zip', { type: 'application/x-zip-compressed' });
    const zipMultipart = new File(['content'], 'test.zip', { type: 'multipart/x-zip' });

    expect(fileIsZip(zipCompressed)).toBe(true);
    expect(fileIsZip(zipMultipart)).toBe(true);
  });

  it('rejects files without .zip extension', () => {
    const notZip = new File(['content'], 'test.txt', { type: 'application/zip' });
    expect(fileIsZip(notZip)).toBe(false);
  });

  it('rejects files without valid ZIP MIME type', () => {
    const wrongMime = new File(['content'], 'test.zip', { type: 'text/plain' });
    expect(fileIsZip(wrongMime)).toBe(false);
  });

  it('handles case-insensitive extension check', () => {
    const upperCase = new File(['content'], 'TEST.ZIP', { type: 'application/zip' });
    const mixedCase = new File(['content'], 'Test.Zip', { type: 'application/zip' });

    expect(fileIsZip(upperCase)).toBe(true);
    expect(fileIsZip(mixedCase)).toBe(true);
  });
});

describe('handleZipFile', () => {
  it('processes ZIP with matching files correctly (one file match)', async () => {
    const zipFile = await createZipFile();
    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(jsonBlueprintA)
    };
    const generalErrors = [];

    await handleZipFile(zipFile, [jsonBlueprintA], blueprintOutcomeMap, generalErrors);

    expect(blueprintOutcomeMap[1].extractedData.length).toBe(2);
    expect(blueprintOutcomeMap[1].extractedData).toContainEqual({ name: 'Alice' });
    expect(generalErrors.length).toBe(0);
  });

  it('processes ZIP with matching files correctly (two file match)', async () => {
    const zipFile = await createZipFile();
    const blueprintOutcomeMap = {
      2: new BlueprintExtractionOutcome(jsonBlueprintBoth)
    };
    const generalErrors = [];

    await handleZipFile(zipFile, [jsonBlueprintBoth], blueprintOutcomeMap, generalErrors);

    expect(blueprintOutcomeMap[2].extractedData.length).toBe(4);
    expect(blueprintOutcomeMap[2].extractedData).toContainEqual({ name: 'Alice' });
    expect(blueprintOutcomeMap[2].extractedData).toContainEqual({ name: 'Diana' });
    expect(generalErrors.length).toBe(0);
  });

  it('registers error when no files match the regex pattern', async () => {
    const zipFile = await createZipFile();
    const noMatchBlueprint = { ...jsonBlueprintA, regex_path: '^no-match\\.json$' };
    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(noMatchBlueprint)
    };
    const generalErrors = [];

    await handleZipFile(zipFile, [noMatchBlueprint], blueprintOutcomeMap, generalErrors);

    expect(blueprintOutcomeMap[1].extractedData.length).toBe(0);
    expect(blueprintOutcomeMap[1].processingErrors.length).toBeGreaterThan(0);
    expect(generalErrors.length).toBe(0);
  });

  it('handles invalid ZIP file gracefully', async () => {
    const invalidZip = new File(['not a zip'], 'fake.zip', { type: 'application/zip' });
    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(jsonBlueprintA)
    };
    const generalErrors = [];

    await handleZipFile(invalidZip, [jsonBlueprintA], blueprintOutcomeMap, generalErrors);

    expect(generalErrors.length).toBeGreaterThan(0);
  });

  it('handles invalid regex pattern in blueprint', async () => {
    const zipFile = await createZipFile();
    const invalidRegexBlueprint = { ...jsonBlueprintA, regex_path: '[invalid(' };
    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(invalidRegexBlueprint)
    };
    const generalErrors = [];

    await handleZipFile(zipFile, [invalidRegexBlueprint], blueprintOutcomeMap, generalErrors);

    expect(blueprintOutcomeMap[1].processingErrors.length).toBeGreaterThan(0);
  });

  it('rejects non-ZIP files based on extension and MIME', async () => {
    const notZip = new File(['content'], 'test.txt', { type: 'text/plain' });
    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(jsonBlueprintA)
    };
    const generalErrors = [];

    await handleZipFile(notZip, [jsonBlueprintA], blueprintOutcomeMap, generalErrors);

    expect(generalErrors.length).toBeGreaterThan(0);
    expect(blueprintOutcomeMap[1].extractedData.length).toBe(0);
  });

  it('processes multiple blueprints with different patterns', async () => {
    const zip = new JSZip();
    zip.file('data_a.json', jsonDataA);
    zip.file('data.csv', csvData);
    const blob = await zip.generateAsync({ type: 'blob' });
    const zipFile = new File([blob], 'multi.zip', { type: 'application/zip' });

    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(jsonBlueprintA),
      3: new BlueprintExtractionOutcome(csvBlueprint)
    };
    const generalErrors = [];

    await handleZipFile(zipFile, [jsonBlueprintA, csvBlueprint], blueprintOutcomeMap, generalErrors);

    expect(blueprintOutcomeMap[1].extractedData.length).toBe(2);
    expect(blueprintOutcomeMap[3].extractedData.length).toBe(2);
    expect(generalErrors.length).toBe(0);
  });
});

describe('handleSingleFile', () => {
  it('processes a single JSON file correctly', async () => {
    const jsonFile = new File([jsonDataA], 'test.json', { type: 'application/json' });
    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(jsonBlueprintA)
    };
    const generalErrors = [];

    await handleSingleFile(jsonFile, [jsonBlueprintA], blueprintOutcomeMap, generalErrors);

    expect(blueprintOutcomeMap[1].extractedData.length).toBe(2);
    expect(blueprintOutcomeMap[1].extractedData[0]).toHaveProperty('name', 'Alice');
  });

  it('processes a single CSV file correctly', async () => {
    const csvFile = new File([csvData], 'test.csv', { type: 'text/csv' });
    const blueprintOutcomeMap = {
      3: new BlueprintExtractionOutcome(csvBlueprint)
    };
    const generalErrors = [];

    await handleSingleFile(csvFile, [csvBlueprint], blueprintOutcomeMap, generalErrors);

    expect(blueprintOutcomeMap[3].extractedData.length).toBe(2);
    expect(blueprintOutcomeMap[3].extractedData[1]).toHaveProperty('name', 'Bob');
  });

  it('applies multiple blueprints to the same file', async () => {
    const jsonFile = new File([jsonDataA], 'test.json', { type: 'application/json' });
    const blueprint2 = { ...jsonBlueprintA, id: 4 };
    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(jsonBlueprintA),
      4: new BlueprintExtractionOutcome(blueprint2)
    };
    const generalErrors = [];

    await handleSingleFile(jsonFile, [jsonBlueprintA, blueprint2], blueprintOutcomeMap, generalErrors);

    expect(blueprintOutcomeMap[1].extractedData.length).toBe(2);
    expect(blueprintOutcomeMap[4].extractedData.length).toBe(2);
  });

  it('handles processing errors for individual blueprints', async () => {
    const invalidJson = new File(['{ invalid json }'], 'bad.json', { type: 'application/json' });
    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(jsonBlueprintA)
    };
    const generalErrors = [];

    await handleSingleFile(invalidJson, [jsonBlueprintA], blueprintOutcomeMap, generalErrors);

    expect(blueprintOutcomeMap[1].processingErrors.length).toBeGreaterThan(0);
  });
});

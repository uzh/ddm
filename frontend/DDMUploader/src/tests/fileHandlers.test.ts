import { describe, it, expect } from 'vitest';
import { handleZipFile, handleSingleFile, fileIsZip, collectZipEntries, stripAppleDoubleSidecars } from '@uploader/composables/useFileProcessor/fileHandlers';
import { BlueprintExtractionOutcome } from '@uploader/classes/BlueprintExtractionOutcome';
import JSZip from 'jszip';
import {matchFilePaths} from "../composables/useFileProcessor/fileHandlers";
import {CSVParserConfig, JSONParserConfig} from "@uploader/types/ParserConfigs";


const JSONConfig: JSONParserConfig = {
  format: 'json',
  extraction_root: '',
  nested_loop_path: '',
  array_join_separator: '\n',
}

const CSVConfig: CSVParserConfig = {
  format: 'csv',
  delimiter: ',',
}

// Blueprint stubs for JSON
const jsonBlueprintA = {
  id: 1,
  name: 'Basic JSON',
  description: 'Tests simple JSON processing',
  format: 'json',
  parser_config: JSONConfig,
  expected_fields: ['name'],
  exp_fields_regex_matching: false,
  nested_expected_fields: [],
  nested_exp_fields_regex_matching: false,
  fields_to_extract: ['name'],
  extraction_fields: [
    {
      id: 1,
      scope: 'root' as const,
      expected_name: 'name',
      match_regex: false,
      keep_in_donation: true,
      alias: null,
    }
  ],
  file_paths: [
    {
      path: 'data_a.json',
      is_regex: false
    }
  ],
  extraction_rules: [
    {
      id: 1,
      field: 'name',
      comparison_operator: null,
      comparison_value: null,
      replacement_value: null
    }
  ],
  is_backup: false,
  backup_ids: [],
};

const jsonBlueprintBoth = {
  ...jsonBlueprintA,
  id: 2,
  name: 'Basic JSON',
  description: 'Tests simple JSON processing',
  file_paths: [
    {
      path: 'data.*\\.json',
      is_regex: true
    }
  ],
};

// CSV Blueprint
const csvBlueprint = {
  ...jsonBlueprintA,
  id: 3,
  format: 'csv',
  parser_config: CSVConfig,
  file_paths: [
    {
      path: '.*\\.csv',
      is_regex: true
    }
  ],
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

// Helper: Create nested ZIP file
async function createNestedZipFile(): Promise<File> {
  const innerZip = new JSZip();
  innerZip.file('inner_data.json', jsonDataB);
  const innerBlob = await innerZip.generateAsync({ type: 'arraybuffer' });

  const outerZip = new JSZip();
  outerZip.file('data_a.json', jsonDataA);
  outerZip.file('nested.zip', innerBlob);

  const blob = await outerZip.generateAsync({ type: 'blob' });
  return new File([blob], 'test.zip', { type: 'application/zip' });
}

// Helper: Create deeply nested ZIP (3 levels)
async function createDeeplyNestedZipFile(): Promise<File> {
  // Level 3 (innermost)
  const level3Zip = new JSZip();
  level3Zip.file('level3_data.json', JSON.stringify([{ name: 'Level3' }]));
  const level3Blob = await level3Zip.generateAsync({ type: 'arraybuffer' });

  // Level 2
  const level2Zip = new JSZip();
  level2Zip.file('level2_data.json', JSON.stringify([{ name: 'Level2' }]));
  level2Zip.file('level3.zip', level3Blob);
  const level2Blob = await level2Zip.generateAsync({ type: 'arraybuffer' });

  // Level 1 (outermost)
  const level1Zip = new JSZip();
  level1Zip.file('level1_data.json', JSON.stringify([{ name: 'Level1' }]));
  level1Zip.file('level2.zip', level2Blob);

  const blob = await level1Zip.generateAsync({ type: 'blob' });
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

    await handleZipFile(zipFile, [jsonBlueprintA], blueprintOutcomeMap, generalErrors, 1);

    expect(blueprintOutcomeMap[1].extractedData.length).toBe(2);
    expect(blueprintOutcomeMap[1].extractedData).toContainEqual({ name: 'Alice' });
    expect(generalErrors.length).toBe(0);
  });

  it('ignores macOS __MACOSX/ AppleDouble sidecar files even when a literal path pattern would otherwise suffix-match them', async () => {
    // Reproduces a real-world zip created on macOS (e.g. via Finder/Archive
    // Utility), which adds a `__MACOSX/<dir>/._<name>` binary resource-fork
    // sidecar next to every real file. A literal (non-regex) BlueprintFilePath
    // like "conversations.json" matches by right-hand-side suffix, so it would
    // also match "__MACOSX/export/._conversations.json" -- whose content is
    // opaque binary metadata, not JSON -- unless these artifacts are filtered
    // out during zip traversal.
    const zip = new JSZip();
    zip.file('export/conversations.json', jsonDataA);
    // Minimal AppleDouble magic-number header; never valid JSON/text.
    zip.file('__MACOSX/export/._conversations.json', new Uint8Array([0x00, 0x05, 0x16, 0x07, 0x00, 0x02, 0x00, 0x00]));
    const blob = await zip.generateAsync({ type: 'blob' });
    const zipFile = new File([blob], 'export.zip', { type: 'application/zip' });

    const literalMatchBlueprint = {
      ...jsonBlueprintA,
      file_paths: [{ path: 'conversations.json', is_regex: false }],
    };
    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(literalMatchBlueprint)
    };
    const generalErrors = [];

    await handleZipFile(zipFile, [literalMatchBlueprint], blueprintOutcomeMap, generalErrors, 1);

    expect(blueprintOutcomeMap[1].extractedData.length).toBe(2);
    expect(blueprintOutcomeMap[1].extractedData).toContainEqual({ name: 'Alice' });
    expect(blueprintOutcomeMap[1].processingErrors).toEqual([]);
    expect(generalErrors.length).toBe(0);
  });

  it('processes ZIP with matching files correctly (two file match)', async () => {
    const zipFile = await createZipFile();
    const blueprintOutcomeMap = {
      2: new BlueprintExtractionOutcome(jsonBlueprintBoth)
    };
    const generalErrors = [];

    await handleZipFile(zipFile, [jsonBlueprintBoth], blueprintOutcomeMap, generalErrors, 1);

    expect(blueprintOutcomeMap[2].extractedData.length).toBe(4);
    expect(blueprintOutcomeMap[2].extractedData).toContainEqual({ name: 'Alice' });
    expect(blueprintOutcomeMap[2].extractedData).toContainEqual({ name: 'Diana' });
    expect(generalErrors.length).toBe(0);
  });

  it('registers error when no files match the regex pattern', async () => {
    const zipFile = await createZipFile();
    const noMatchBlueprint = {
      ...jsonBlueprintA,
      file_paths: [
        {
          path: '^no-match\\.json$',
          is_regex: true
        }
      ],
    };
    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(noMatchBlueprint)
    };
    const generalErrors = [];

    await handleZipFile(zipFile, [noMatchBlueprint], blueprintOutcomeMap, generalErrors, 1);

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

    await handleZipFile(invalidZip, [jsonBlueprintA], blueprintOutcomeMap, generalErrors, 1);

    expect(generalErrors.length).toBeGreaterThan(0);
  });

  it('handles invalid regex pattern in blueprint', async () => {
    const zipFile = await createZipFile();
    const invalidRegexBlueprint = {
      ...jsonBlueprintA,
      file_paths: [
        {
          path: '[invalid(',
          is_regex: true
        }
      ],
    };
    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(invalidRegexBlueprint)
    };
    const generalErrors = [];

    await handleZipFile(zipFile, [invalidRegexBlueprint], blueprintOutcomeMap, generalErrors, 1);

    expect(blueprintOutcomeMap[1].processingErrors.length).toBeGreaterThan(0);
  });

  it('rejects non-ZIP files based on extension and MIME', async () => {
    const notZip = new File(['content'], 'test.txt', { type: 'text/plain' });
    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(jsonBlueprintA)
    };
    const generalErrors = [];

    await handleZipFile(notZip, [jsonBlueprintA], blueprintOutcomeMap, generalErrors, 1);

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

    await handleZipFile(zipFile, [jsonBlueprintA, csvBlueprint], blueprintOutcomeMap, generalErrors, 1);

    expect(blueprintOutcomeMap[1].extractedData.length).toBe(2);
    expect(blueprintOutcomeMap[3].extractedData.length).toBe(2);
    expect(generalErrors.length).toBe(0);
  });
});

describe('collectZipEntries (via handleZipFile)', () => {
  // Blueprint that matches any JSON file
  const anyJsonBlueprint = {
    ...jsonBlueprintA,
    id: 10,
    file_paths: [
        {
          path: '.*\\.json$',
          is_regex: true
        }
      ],
  };

  it('extracts files from nested ZIP archives', async () => {
    const zipFile = await createNestedZipFile();
    const blueprintOutcomeMap = {
      10: new BlueprintExtractionOutcome(anyJsonBlueprint)
    };
    const generalErrors = [];
    const maxDepth = 3;

    await handleZipFile(zipFile, [anyJsonBlueprint], blueprintOutcomeMap, generalErrors, maxDepth);

    // Should find data_a.json from outer and inner_data.json from nested.zip
    expect(blueprintOutcomeMap[10].extractedData.length).toBe(4); // 2 from outer + 2 from inner
    expect(blueprintOutcomeMap[10].extractedData).toContainEqual({ name: 'Alice' });
    expect(blueprintOutcomeMap[10].extractedData).toContainEqual({ name: 'Chester' });
    expect(generalErrors.length).toBe(0);
  });

  it('builds correct paths for files in nested ZIPs', async () => {
    const zipFile = await createNestedZipFile();
    // Blueprint specifically matching nested path pattern
    const nestedPathBlueprint = {
      ...jsonBlueprintA,
      id: 11,
      file_paths: [
        {
          path: 'nested\\.zip/inner_data\\.json',
          is_regex: true
        }
      ],
    };
    const blueprintOutcomeMap = {
      11: new BlueprintExtractionOutcome(nestedPathBlueprint)
    };
    const generalErrors = [];
    const maxDepth = 3;

    await handleZipFile(zipFile, [nestedPathBlueprint], blueprintOutcomeMap, generalErrors, maxDepth);

    expect(blueprintOutcomeMap[11].extractedData.length).toBe(2);
    expect(blueprintOutcomeMap[11].extractedData).toContainEqual({ name: 'Chester' });
    expect(generalErrors.length).toBe(0);
  });

  it('processes deeply nested ZIPs up to max depth (3 levels)', async () => {
    const zipFile = await createDeeplyNestedZipFile();
    const blueprintOutcomeMap = {
      10: new BlueprintExtractionOutcome(anyJsonBlueprint)
    };
    const generalErrors = [];
    const maxDepth = 3;

    await handleZipFile(zipFile, [anyJsonBlueprint], blueprintOutcomeMap, generalErrors, maxDepth);

    // Should extract from all 3 levels
    const names = blueprintOutcomeMap[10].extractedData.map(d => d.name);

    expect(names).toContain('Level1');
    expect(names).toContain('Level2');
    expect(names).toContain('Level3');
    expect(generalErrors.length).toBe(0);
  });

  it('does not process ZIPs nested beyond max depth', async () => {
    const zipFile = await createDeeplyNestedZipFile();
    const blueprintOutcomeMap = {
      10: new BlueprintExtractionOutcome(anyJsonBlueprint)
    };
    const generalErrors = [];
    const maxDepth = 1;

    await handleZipFile(zipFile, [anyJsonBlueprint], blueprintOutcomeMap, generalErrors, maxDepth);

    const names = blueprintOutcomeMap[10].extractedData.map(d => d.name);
    expect(names).toContain('Level1');
    expect(names).toContain('Level2');
    expect(names).not.toContain('Level3');
  });

  it('handles corrupted nested ZIP gracefully', async () => {
    const outerZip = new JSZip();
    outerZip.file('data.json', jsonDataA);
    outerZip.file('corrupted.zip', 'not valid zip content');

    const blob = await outerZip.generateAsync({ type: 'blob' });
    const zipFile = new File([blob], 'test.zip', { type: 'application/zip' });

    const blueprintOutcomeMap = {
      10: new BlueprintExtractionOutcome(anyJsonBlueprint)
    };
    const generalErrors = [];
    const maxDepth = 3;

    await handleZipFile(zipFile, [anyJsonBlueprint], blueprintOutcomeMap, generalErrors, maxDepth);

    // Should still process valid files and register error for corrupted nested ZIP
    expect(blueprintOutcomeMap[10].extractedData.length).toBe(2);
    expect(generalErrors.length).toBeGreaterThan(0);
  });

  it('handles nested ZIPs in subdirectories', async () => {
    const innerZip = new JSZip();
    innerZip.file('deep_data.json', JSON.stringify([{ name: 'DeepFile' }]));
    const innerBlob = await innerZip.generateAsync({ type: 'arraybuffer' });

    const outerZip = new JSZip();
    outerZip.file('root.json', jsonDataA);
    outerZip.file('subdir/nested.zip', innerBlob);

    const blob = await outerZip.generateAsync({ type: 'blob' });
    const zipFile = new File([blob], 'test.zip', { type: 'application/zip' });

    const blueprintOutcomeMap = {
      10: new BlueprintExtractionOutcome(anyJsonBlueprint)
    };
    const generalErrors = [];
    const maxDepth = 3;

    await handleZipFile(zipFile, [anyJsonBlueprint], blueprintOutcomeMap, generalErrors, maxDepth);

    const names = blueprintOutcomeMap[10].extractedData.map(d => d.name);
    expect(names).toContain('Alice');
    expect(names).toContain('DeepFile');
  });

  it('skips directory entries in ZIP', async () => {
    const zip = new JSZip();
    zip.file('folder/', null, { dir: true });
    zip.file('folder/data.json', jsonDataA);
    zip.file('empty_folder/', null, { dir: true });

    const blob = await zip.generateAsync({ type: 'blob' });
    const zipFile = new File([blob], 'test.zip', { type: 'application/zip' });

    const blueprintOutcomeMap = {
      10: new BlueprintExtractionOutcome(anyJsonBlueprint)
    };
    const generalErrors = [];
    const maxDepth = 3;

    await handleZipFile(zipFile, [anyJsonBlueprint], blueprintOutcomeMap, generalErrors, maxDepth);

    // Should only process the actual file, not directories
    expect(blueprintOutcomeMap[10].extractedData.length).toBe(2);
    expect(generalErrors.length).toBe(0);
  });
});

describe('collectZipEntries (test in isolation)', () => {

  it('creates correct entries from ZIP archives without extracting nested', async () => {
    const zip = await createNestedZipFile();
    const zipFile = await JSZip.loadAsync(zip);
    const generalErrors = [];
    const maxDepth = 0;

    const entries = await collectZipEntries(zipFile, generalErrors, maxDepth);
    const fullPaths = entries.map(entry => entry.fullPath);

    expect(entries.length).toBe(2);
    expect(fullPaths).toContainEqual('nested.zip');
    expect(fullPaths).toContainEqual('data_a.json');
    expect(generalErrors.length).toBe(0);
  });

  it('filters out any entry inside a top-level __MACOSX/ directory', async () => {
    const zip = new JSZip();
    zip.file('data_a.json', jsonDataA);
    zip.file('__MACOSX/data_a.json', new Uint8Array([0x00, 0x05, 0x16, 0x07]));
    zip.file('__MACOSX/._data_a.json', new Uint8Array([0x00, 0x05, 0x16, 0x07]));
    const zipFile = await JSZip.loadAsync(await zip.generateAsync({ type: 'blob' }));
    const generalErrors = [];

    const entries = await collectZipEntries(zipFile, generalErrors, 0);
    const fullPaths = entries.map(entry => entry.fullPath);

    expect(fullPaths).toEqual(['data_a.json']);
    expect(generalErrors.length).toBe(0);
  });

  it('creates correct entries from deeply nested ZIP archives', async () => {
    const zip = await createDeeplyNestedZipFile();
    const zipFile = await JSZip.loadAsync(zip);
    const generalErrors = [];
    const maxDepth = 4;

    const entries = await collectZipEntries(zipFile, generalErrors, maxDepth);
    const fullPaths = entries.map(entry => entry.fullPath);

    expect(entries.length).toBe(3);
    expect(fullPaths).toContainEqual('level1_data.json');
    expect(fullPaths).toContainEqual('level2.zip/level2_data.json');
    expect(fullPaths).toContainEqual('level2.zip/level3.zip/level3_data.json');
    expect(generalErrors.length).toBe(0);
  });

  it('creates correct entries from overly nested ZIP archives', async () => {
    const zip = await createDeeplyNestedZipFile();
    const zipFile = await JSZip.loadAsync(zip);
    const generalErrors = [];
    const maxDepth = 1;

    const entries = await collectZipEntries(zipFile, generalErrors, maxDepth);
    const fullPaths = entries.map(entry => entry.fullPath);

    expect(entries.length).toBe(3);
    expect(fullPaths).toContainEqual('level1_data.json');
    expect(fullPaths).toContainEqual('level2.zip/level2_data.json');
    expect(fullPaths).toContainEqual('level2.zip/level3.zip');
    expect(generalErrors.length).toBe(0);
  });

});

describe('stripAppleDoubleSidecars', () => {
  it('removes a ._-prefixed file when a real sibling of the same name exists', () => {
    const entries = [
      { fullPath: 'subdir/data_a.json', entry: {} as any },
      { fullPath: 'subdir/._data_a.json', entry: {} as any },
    ];

    const result = stripAppleDoubleSidecars(entries);

    expect(result.map(e => e.fullPath)).toEqual(['subdir/data_a.json']);
  });

  it('preserves a genuinely-named ._-prefixed file that has no matching sibling', () => {
    // A file that happens to be named "._config.json" with no plain
    // "config.json" alongside it is indistinguishable from real user data
    // and must not be silently dropped.
    const entries = [
      { fullPath: 'subdir/._config.json', entry: {} as any },
      { fullPath: 'subdir/unrelated.json', entry: {} as any },
    ];

    const result = stripAppleDoubleSidecars(entries);

    expect(result.map(e => e.fullPath).sort()).toEqual([
      'subdir/._config.json',
      'subdir/unrelated.json',
    ]);
  });

  it('only matches siblings within the same directory', () => {
    const entries = [
      { fullPath: 'dir_a/data.json', entry: {} as any },
      { fullPath: 'dir_b/._data.json', entry: {} as any },
    ];

    const result = stripAppleDoubleSidecars(entries);

    // No sibling in dir_b itself, so the ._-prefixed file is kept.
    expect(result.map(e => e.fullPath).sort()).toEqual([
      'dir_a/data.json',
      'dir_b/._data.json',
    ]);
  });
});

describe('matchFilePaths', () => {
  const testBlueprint = {
    ...jsonBlueprintA,
    id: 11,
    file_paths: [
        {
          path: 'irrelevant path for this unit test',
          is_regex: true
        }
      ],
  };
  const zipPaths = ['folder/file.json', 'file.json'];

  const testOutcomeMap = {
    11: new BlueprintExtractionOutcome(testBlueprint)
  };

  it('matches regex pattern correctly (single match)', async () => {
    const blueprintFilePaths = [{path: 'folder.*\\.json$', is_regex: true}]
    const result = matchFilePaths(zipPaths, blueprintFilePaths, testBlueprint.id, testOutcomeMap);
    expect(result.length).toBe(1);
    expect(result).toContain('folder/file.json');
  });

  it('matches regex pattern correctly (multiple matches)', async () => {
    const blueprintFilePaths = [{path: '.*\\.json$', is_regex: true}]
    const result = matchFilePaths(zipPaths, blueprintFilePaths, testBlueprint.id, testOutcomeMap);
    expect(result.length).toBe(2);
    expect(result).toContain('folder/file.json');
    expect(result).toContain('file.json');
  });

  it('matches regular pattern correctly (right-hand partial)', async () => {
    const blueprintFilePaths = [{path: '/file.json', is_regex: false}]
    const result = matchFilePaths(zipPaths, blueprintFilePaths, testBlueprint.id, testOutcomeMap);
    expect(result.length).toBe(1);
    expect(result).toContain('folder/file.json');
  });

  it('matches regular pattern correctly (full path)', async () => {
    const blueprintFilePaths = [{path: 'folder/file.json', is_regex: false}]
    const result = matchFilePaths(zipPaths, blueprintFilePaths, testBlueprint.id, testOutcomeMap);
    expect(result.length).toBe(1);
    expect(result).toContain('folder/file.json');
  });

  it('matches regular pattern correctly (multiple files)', async () => {
    const blueprintFilePaths = [{path: 'file.json', is_regex: false}]
    const result = matchFilePaths(zipPaths, blueprintFilePaths, testBlueprint.id, testOutcomeMap);
    expect(result.length).toBe(2);
    expect(result).toContain('folder/file.json');
    expect(result).toContain('file.json');
  });

  it('handles no match gracefully', async () => {
    const blueprintFilePaths = [{path: 'file-non-existing.json', is_regex: false}]
    const result = matchFilePaths(zipPaths, blueprintFilePaths, testBlueprint.id, testOutcomeMap);
    expect(result.length).toBe(0);
    expect(testOutcomeMap[11].processingErrors.length).toBe(0);
  });

  it('respects blueprint file path order', async () => {
    const blueprintFilePaths = [
      {path: 'folder/file.json', is_regex: false},
      {path: '*.json', is_regex: true},
    ]
    const result = matchFilePaths(zipPaths, blueprintFilePaths, testBlueprint.id, testOutcomeMap);
    expect(result.length).toBe(1);
    expect(result).toContain('folder/file.json');
  });

  it('handles many blueprint file paths correctly', async () => {
    const blueprintFilePaths = [
      {path: '123', is_regex: false},
      {path: '456', is_regex: false},
      {path: 'abc', is_regex: false},
      {path: 'def', is_regex: false},
      {path: 'gh12', is_regex: false},
      {path: 'folder/file.json', is_regex: false},
    ]
    const result = matchFilePaths(zipPaths, blueprintFilePaths, testBlueprint.id, testOutcomeMap);
    expect(result.length).toBe(1);
    expect(result).toContain('folder/file.json');
  });

  it('handles invalid regex pattern gracefully', async () => {
    const blueprintFilePaths = [{path: '[invalid(', is_regex: true}];
    const testInternalOutcomeMap = {11: new BlueprintExtractionOutcome(testBlueprint)};
    const result = matchFilePaths(zipPaths, blueprintFilePaths, testBlueprint.id, testInternalOutcomeMap);
    expect(result.length).toBe(0);
    expect(testInternalOutcomeMap[11].processingErrors.length).toBe(1);
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

  it('strips a leading UTF-8 BOM before parsing, rather than failing on it', async () => {
    const jsonFileWithBom = new File(['﻿' + jsonDataA], 'test.json', { type: 'application/json' });
    const blueprintOutcomeMap = {
      1: new BlueprintExtractionOutcome(jsonBlueprintA)
    };
    const generalErrors = [];

    await handleSingleFile(jsonFileWithBom, [jsonBlueprintA], blueprintOutcomeMap, generalErrors);

    expect(blueprintOutcomeMap[1].processingErrors).toEqual([]);
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

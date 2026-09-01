import { defineComponent, h } from 'vue';
import { mount } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import en from '@uploader/locales/en.json';
import { useLogPoster } from '@uploader/composables/useLogPoster';
import { BlueprintExtractionOutcome } from '@uploader/classes/BlueprintExtractionOutcome';
import { ERROR_CATALOG } from '@uploader/utils/errorCatalog';
import { registerGeneralError } from '@uploader/composables/useFileProcessor/errorHandling';
import { Blueprint } from '@uploader/types/Blueprint';

const EXCEPTION_URL = 'https://example.com/p/api/exceptions/';
const UPLOADER_ID = 7;

function buildBlueprint(): Blueprint {
  return {
    id: 42,
    name: 'bp',
    description: '',
    format: 'json',
    parser_config: { format: 'json', extraction_root: '', nested_loop_path: '', array_join_separator: '\n', max_root_entries: null },
    expected_fields: [],
    exp_fields_regex_matching: false,
    nested_expected_fields: [],
    nested_exp_fields_regex_matching: false,
    nested_entry_exclusion_allowed: false,
    nested_display_by_root_item: false,
    fields_to_extract: ['name'],
    extraction_fields: [],
    file_paths: [],
    extraction_rules: [],
    is_backup: false,
    backup_ids: [],
  };
}

function mountPoster() {
  const i18n = createI18n({ legacy: false, locale: 'en', fallbackLocale: 'en', messages: { en } });
  const Component = defineComponent({
    setup() {
      return useLogPoster(UPLOADER_ID, EXCEPTION_URL);
    },
    render() { return h('div'); },
  });
  return mount(Component, { global: { plugins: [i18n] } });
}

/** Parsed JSON bodies of every fetch() POST, in call order. */
function postedBodies(): any[] {
  return (fetch as any).mock.calls.map((c: any[]) => JSON.parse(c[1].body));
}

/** The body posted for a given status_code. */
function bodyFor(statusCode: string): any {
  return postedBodies().find(b => b.status_code === statusCode);
}

describe('useLogPoster', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn(async () => ({ ok: true, status: 201, statusText: 'Created' })));
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('serializes EXTRACTED_FIELDS_MAP as a real object, not "{}"', async () => {
    const outcome = new BlueprintExtractionOutcome(buildBlueprint());
    outcome.mapExtractedKey('name', 'user_name');
    outcome.mapExtractedKey('email', 'contact.email');

    await mountPoster().vm.postLogs([], { 42: outcome });

    const body = bodyFor('EXTRACTED_FIELDS_MAP');
    expect(body.message).not.toBe('{}');
    expect(JSON.parse(body.message)).toEqual({ name: 'user_name', email: 'contact.email' });
  });

  it('posts ZIP_READ_FAIL as its structured context (reader error + nested path)', async () => {
    const generalErrors: any[] = [];
    registerGeneralError(generalErrors, ERROR_CATALOG.ZIP_READ_FAIL, {
      error: 'Corrupted zip: missing bytes',
      nestedZipPath: 'takeout/archive.zip',
      depth: 1,
    });

    await mountPoster().vm.postLogs(generalErrors, {});

    const body = bodyFor('ZIP_READ_FAIL');
    expect(body.blueprint).toBeNull();
    const detail = JSON.parse(body.message);
    expect(detail.error).toBe('Corrupted zip: missing bytes');
    expect(detail.nestedZipPath).toBe('takeout/archive.zip');
    expect(detail.depth).toBe(1);
  });

  it('still posts other general errors as their translated string', async () => {
    const generalErrors: any[] = [];
    registerGeneralError(generalErrors, ERROR_CATALOG.INVALID_ZIP, { fileType: 'txt' });

    await mountPoster().vm.postLogs(generalErrors, {});

    const body = bodyFor('INVALID_ZIP');
    expect(body.message).toBe(en.errors['invalid-zip'].replace('{fileType}', 'txt'));
  });

  it('keeps the log payload shape (uploader / raised_by / date / blueprint)', async () => {
    const outcome = new BlueprintExtractionOutcome(buildBlueprint());

    await mountPoster().vm.postLogs([], { 42: outcome });

    const body = bodyFor('EXTRACTION_STATS');
    expect(body.uploader).toBe(UPLOADER_ID);
    expect(body.raised_by).toBe('client');
    expect(body.blueprint).toBe(42);
    expect(typeof body.date).toBe('string');
    expect(Number.isNaN(Date.parse(body.date))).toBe(false);
  });
});

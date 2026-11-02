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

/** The single bundled body posted by the given fetch call index (default: the first/only call). */
function postedBundle(callIndex = 0): any {
  return JSON.parse((fetch as any).mock.calls[callIndex][1].body);
}

/** The log entry within the posted bundle matching a given status_code. */
function entryFor(statusCode: string, callIndex = 0): any {
  return postedBundle(callIndex).logs.find((l: any) => l.status_code === statusCode);
}

describe('useLogPoster', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn(async () => ({ ok: true, status: 201, statusText: 'Created' })));
  });
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it('serializes EXTRACTED_FIELDS_MAP as a real object, not "{}"', async () => {
    const outcome = new BlueprintExtractionOutcome(buildBlueprint());
    outcome.mapExtractedKey('name', 'user_name');
    outcome.mapExtractedKey('email', 'contact.email');

    await mountPoster().vm.postLogs([], { 42: outcome });

    const entry = entryFor('EXTRACTED_FIELDS_MAP');
    expect(entry.message).not.toBe('{}');
    expect(JSON.parse(entry.message)).toEqual({ name: 'user_name', email: 'contact.email' });
  });

  it('posts ZIP_READ_FAIL as its structured context (reader error + nested path)', async () => {
    const generalErrors: any[] = [];
    registerGeneralError(generalErrors, ERROR_CATALOG.ZIP_READ_FAIL, {
      error: 'Corrupted zip: missing bytes',
      nestedZipPath: 'takeout/archive.zip',
      depth: 1,
    });

    await mountPoster().vm.postLogs(generalErrors, {});

    const entry = entryFor('ZIP_READ_FAIL');
    expect(entry.blueprint).toBeNull();
    const detail = JSON.parse(entry.message);
    expect(detail.error).toBe('Corrupted zip: missing bytes');
    expect(detail.nestedZipPath).toBe('takeout/archive.zip');
    expect(detail.depth).toBe(1);
  });

  it('still posts other general errors as their translated string', async () => {
    const generalErrors: any[] = [];
    registerGeneralError(generalErrors, ERROR_CATALOG.INVALID_ZIP, { fileType: 'txt' });

    await mountPoster().vm.postLogs(generalErrors, {});

    const entry = entryFor('INVALID_ZIP');
    expect(entry.message).toBe(en.errors['invalid-zip'].replace('{fileType}', 'txt'));
  });

  it('keeps the log entry shape (uploader / blueprint) and a top-level batch date', async () => {
    const outcome = new BlueprintExtractionOutcome(buildBlueprint());

    await mountPoster().vm.postLogs([], { 42: outcome });

    const entry = entryFor('EXTRACTION_STATS');
    expect(entry.uploader).toBe(UPLOADER_ID);
    expect(entry.blueprint).toBe(42);
    // raised_by is no longer sent by the client - it's hardcoded server
    // side, since this endpoint is only ever called by this frontend.
    expect(entry.raised_by).toBeUndefined();

    const bundle = postedBundle();
    expect(typeof bundle.date).toBe('string');
    expect(Number.isNaN(Date.parse(bundle.date))).toBe(false);
  });

  it('posts exactly one fetch call per postLogs() invocation, bundling every entry', async () => {
    const generalErrors: any[] = [];
    registerGeneralError(generalErrors, ERROR_CATALOG.INVALID_ZIP, { fileType: 'txt' });
    const outcome = new BlueprintExtractionOutcome(buildBlueprint());

    await mountPoster().vm.postLogs(generalErrors, { 42: outcome });

    expect((fetch as any).mock.calls.length).toBe(1);
    // 1 general error + 3 fixed per-blueprint logs (no processing errors on
    // this outcome).
    expect(postedBundle().logs.length).toBe(4);
  });

  it('makes no fetch call at all when there is nothing to log', async () => {
    await mountPoster().vm.postLogs([], {});

    expect((fetch as any).mock.calls.length).toBe(0);
  });

  it('retries once on failure then succeeds, without throwing', async () => {
    let callCount = 0;
    vi.stubGlobal('fetch', vi.fn(async () => {
      callCount++;
      if (callCount === 1) {
        return { ok: false, status: 500, statusText: 'Server Error' };
      }
      return { ok: true, status: 201, statusText: 'Created' };
    }));
    vi.useFakeTimers();

    const outcome = new BlueprintExtractionOutcome(buildBlueprint());
    const promise = mountPoster().vm.postLogs([], { 42: outcome });
    await vi.runAllTimersAsync();
    await expect(promise).resolves.toBeUndefined();

    expect((fetch as any).mock.calls.length).toBe(2);
  });

  it('gives up after exhausting all attempts, logs to console, and still does not throw', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => ({ ok: false, status: 500, statusText: 'Server Error' })));
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.useFakeTimers();

    const outcome = new BlueprintExtractionOutcome(buildBlueprint());
    const promise = mountPoster().vm.postLogs([], { 42: outcome });
    await vi.runAllTimersAsync();
    await expect(promise).resolves.toBeUndefined();

    expect((fetch as any).mock.calls.length).toBe(3);
    expect(consoleErrorSpy).toHaveBeenCalled();
  });
});

// src/composables/usePersistedRef.ts
import { ref, watch, } from 'vue'
import { QuestionnaireConfig } from "@questionnaire/types/questionnaire";

/**
 * Produces a short, deterministic hash string representing the *structural*
 * shape of a questionnaire config, for use as a cache-invalidation version
 * key (e.g. alongside persisted `responses`/`currentPage` in localStorage).
 *
 * Included in the hash (changes here WILL invalidate cached data):
 * - Which questions exist (`question` id), their `page`, `type`, and `required` flag.
 * - Which items exist per question (by `item.id`) and which scale points exist
 *   per question (by `scale.value`).
 * - `options` (e.g. `input_type`, `display`, `max_input_length`, ...).
 *
 * Deliberately excluded from the hash (changes here will NOT invalidate
 * cached data — a copy edit should not wipe a user's in-progress answers):
 * - Display copy: `text`, `label`, `label_alt`, `input_label`, `heading_label`.
 *
 * Order-independent by design: `questionnaireConfig` (and each question's
 * `items`/`scale`) may be randomized per render (e.g. shuffled answer order),
 * so both the question list and each question's `items`/`scale` are sorted
 * by a stable identifier (`question` id, `item.id`, `scale.value`) before
 * hashing. This means shuffled presentation order never produces a
 * different hash — only actual additions, removals, or type/option changes do.
 *
 * Not cryptographic — this is a simple string hash intended only to detect
 * "did the structural config change since last time".
 */
function hashConfig(config: QuestionnaireConfig): string {
  const structural = config
    .map((q) => ({
      question: q.question,
      page: q.page,
      type: q.type,
      required: q.required ?? false,
      items: q.items
        ? [...q.items].map((i) => i.id).sort()
        : undefined,
      scale: q.scale
        ? [...q.scale].map((s) => s.value).sort((a, b) => a - b)
        : undefined,
      options: q.options ?? undefined,
    }))
    .sort((a, b) => a.question.localeCompare(b.question)) // stable order regardless of runtime randomization

  const str = JSON.stringify(structural)
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = (hash * 31 + str.charCodeAt(i)) | 0
  }
  return hash.toString(36)
}

export function usePersistedRef<T>(
  key: string,
  defaultValue: T,
  ttlMs: number,
  versionSource?: QuestionnaireConfig
) {
  const currentVersion = versionSource !== undefined ? hashConfig(versionSource) : '1'

  function load(): T {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) throw new Error('empty');
      const parsed = JSON.parse(raw);
      if (parsed.version !== currentVersion) throw new Error('stale version');
      if (Date.now() > parsed.expiresAt) throw new Error('expired');
      return parsed.value;
    } catch {
      localStorage.removeItem(key)
      return defaultValue;
    }
  }

  const state = ref<T>(load());

  watch(state, (value) => {
    localStorage.setItem(key, JSON.stringify({
      version: currentVersion,
      expiresAt: Date.now() + ttlMs,
      value,
    }))
  }, { deep: true })

  function clearProgress() {
    localStorage.removeItem(key);
  }

  return { state, clearProgress }
}

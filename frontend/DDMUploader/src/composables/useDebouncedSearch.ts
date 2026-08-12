import {ref, watch} from "vue";
import {debounce} from "@uploader/utils/debounce";

/**
 * useDebouncedSearch
 *
 * A `term` ref for v-model binding, and a `debouncedTerm` (lowercased) that
 * updates delayMs after `term` stops changing.
 */
export function useDebouncedSearch(delayMs = 300) {
  const term = ref('');
  const debouncedTerm = ref('');
  const update = debounce((v: string) => { debouncedTerm.value = v.toLowerCase(); }, delayMs);
  watch(term, update);
  return { term, debouncedTerm };
}

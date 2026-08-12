import {ref, watch} from "vue";
import {debounce} from "@uploader/utils/debounce";

export function useDebouncedSearch(delayMs = 300) {
  const term = ref('');
  const debouncedTerm = ref('');
  const update = debounce((v: string) => { debouncedTerm.value = v.toLowerCase(); }, delayMs);
  watch(term, update);
  return { term, debouncedTerm };
}

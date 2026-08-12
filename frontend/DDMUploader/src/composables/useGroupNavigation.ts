import {computed, Ref, ref, watch} from "vue";
import {EntryGroup} from "@uploader/utils/entryGroup";

/**
 * useGroupNavigation
 *
 * Tracks the current index into `groups` and steps prev/next through it. If
 * `isFiltered` is true, stepping instead moves between the indices listed
 * in `matchingIndices` (skipping non-matching groups in between), and jumps
 * to the first match if the current index falls out of the match set.
 */
export function useGroupNavigation(groups: Ref<EntryGroup[]>, matchingIndices: Ref<number[]>, isFiltered: Ref<boolean>) {
  const currentIndex = ref(0);
  const currentMatchPosition = computed(() => matchingIndices.value.indexOf(currentIndex.value));

  const canGoPrev = computed(() => isFiltered.value ? currentMatchPosition.value > 0 : currentIndex.value > 0);
  const canGoNext = computed(() => isFiltered.value
    ? currentMatchPosition.value !== -1 && currentMatchPosition.value < matchingIndices.value.length - 1
    : currentIndex.value < groups.value.length - 1);

  const next = () => { if (!canGoNext.value) return; currentIndex.value = isFiltered.value ? matchingIndices.value[currentMatchPosition.value + 1] : currentIndex.value + 1; };
  const prev = () => { if (!canGoPrev.value) return; currentIndex.value = isFiltered.value ? matchingIndices.value[currentMatchPosition.value - 1] : currentIndex.value - 1; };

  watch(matchingIndices, (indices) => {
    if (!isFiltered.value || indices.length === 0) return;
    if (!indices.includes(currentIndex.value)) currentIndex.value = indices[0];
  });

  return { currentIndex, currentMatchPosition, canGoPrev, canGoNext, next, prev };
}

import {computed, Ref, ref, watch} from "vue";
import {EntryGroup} from "@uploader/utils/entryGroup";

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

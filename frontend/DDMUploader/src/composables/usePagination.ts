import {computed, Ref, ref, watch} from "vue";

/**
 * usePagination
 *
 * Tracks the current page over `itemCount` items at `pageSize` per page,
 * clamping the page when itemCount shrinks. next/prev also reset
 * `scrollTarget`'s scroll position, if given.
 */
export function usePagination(itemCount: Ref<number>, pageSize = 20, scrollTarget?: Ref<HTMLElement | null>) {
  const currentPage = ref(1);
  const maxPage = computed(() => Math.ceil(itemCount.value / pageSize));
  const lowerPosition = computed(() => Math.max((currentPage.value - 1) * pageSize, 0));
  const upperPosition = computed(() => Math.min(itemCount.value, lowerPosition.value + pageSize));

  watch(maxPage, () => {
    currentPage.value = Math.min(Math.max(currentPage.value, 1), Math.max(maxPage.value, 1));
  }, { immediate: true });

  const next = () => { if (currentPage.value < maxPage.value) { currentPage.value++; scrollTarget?.value && (scrollTarget.value.scrollTop = 0); } };
  const prev = () => { if (currentPage.value > 1) { currentPage.value--; scrollTarget?.value && (scrollTarget.value.scrollTop = 0); } };

  return { currentPage, maxPage, lowerPosition, upperPosition, next, prev };
}

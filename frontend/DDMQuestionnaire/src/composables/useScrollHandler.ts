import {onBeforeUnmount, onMounted, Ref, ref} from 'vue';
import {getHeightOfLastQuestionTextBefore} from "@questionnaire/utils/scrollFunctions";

/**
 * Composable handling automated scrolling behaviour.
 */
export function useScrollHandler(rootElement: Ref<HTMLElement | null>) {
  const highlightUntilWidth: number = 768;
  const shouldHighlightOnScroll = ref<boolean>(window.innerWidth <= highlightUntilWidth);

  onMounted(() => {
    updateShouldHighlightOnScroll();
    registerScrollEvents();
  });

  onBeforeUnmount(() => {
    removeScrollEvents();
  });

  /**
   * Binds scroll-related event listeners.
   */
  function registerScrollEvents(): void {
    window.addEventListener('resize', updateShouldHighlightOnScroll);
    window.addEventListener('scroll', updateMostVisibleRow);
    window.addEventListener('load', updateMostVisibleRow);
  }

  /**
   * Cleans up scroll-related event listeners.
   */
  function removeScrollEvents(): void {
    window.removeEventListener('resize', () => {});
    window.removeEventListener('scroll', updateMostVisibleRow);
    window.removeEventListener('load', updateMostVisibleRow);
  }

  /**
   * Updates the `shouldHighlightOnScroll` flag depending on screen width.
   */
  function updateShouldHighlightOnScroll(): void {
    shouldHighlightOnScroll.value = window.innerWidth <= highlightUntilWidth;
  }

  /**
   * Highlights the most visible `.response-row` element in the viewport by setting its opacity to `1`,
   * while dimming all others by setting their opacity to `0.3`.
   *
   * If `shouldHighlightOnScroll` is false, all rows remain fully visible.
   */
  function updateMostVisibleRow(): void {
    const root = rootElement.value;
    const responseRows = Array.from(root.querySelectorAll<HTMLElement>('.response-row'));
    let mostVisibleRow: HTMLElement | null = null;
    let minDistance = Infinity;

    if (!shouldHighlightOnScroll.value) {
      responseRows.forEach(row => (row.style.opacity = "1"));
      return;
    }

    responseRows.forEach(row => {
      const rect = row.getBoundingClientRect();
      const questionHeight = getHeightOfLastQuestionTextBefore(row);
      const distance = Math.abs(rect.top);

      const isVisible = rect.bottom > 0 && rect.top < window.innerHeight && rect.top >= (questionHeight * 0.25);

      if (isVisible && distance < minDistance) {
        minDistance = distance;
        mostVisibleRow = row;
      }
    });

    responseRows.forEach(row => (row.style.opacity = "0.3"));
    if (mostVisibleRow) {
      mostVisibleRow.style.opacity = "1";
    }
  }

  /**
   * Smoothly scrolls the page to the top, after DOM updates.
   * Uses a short delay to ensure layout is settled.
   */
  function scrollToTop(): void {
    setTimeout(() => {
      document.documentElement.scrollTo({
        top: 0,
        behavior: 'smooth',
      });
      // Fallbacks for compatibility
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    }, 100);
  }

  return {
    scrollToTop
  }
}

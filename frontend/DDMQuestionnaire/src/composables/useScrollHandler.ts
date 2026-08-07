import { onBeforeUnmount, onMounted, ref } from 'vue';

/**
 * Composable handling automated scrolling behaviour.
 */
export function useScrollHandler() {
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
  }

  /**
   * Cleans up scroll-related event listeners.
   */
  function removeScrollEvents(): void {
    window.removeEventListener('resize', () => {});
  }

  /**
   * Updates the `shouldHighlightOnScroll` flag depending on screen width.
   */
  function updateShouldHighlightOnScroll(): void {
    shouldHighlightOnScroll.value = window.innerWidth <= highlightUntilWidth;
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

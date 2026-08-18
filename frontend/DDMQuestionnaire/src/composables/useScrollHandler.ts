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
      const target = document.documentElement;
      const overlay = document.querySelector('#qapp');

      const cleanup = () => {
        overlay?.classList.remove('scrolling-overlay');
        target.removeEventListener('scrollend', cleanup);
      };

      // Already at top — nothing will scroll, so scrollend won't fire. Skip straight to cleanup.
      if (target.scrollTop === 0 && document.body.scrollTop === 0) {
        overlay?.classList.remove('scrolling-overlay');
        return;
      }

      overlay?.classList.add('scrolling-overlay');

      if ('onscrollend' in window) {
        window.addEventListener('scrollend', cleanup);
      } else {
        setTimeout(cleanup, 200);
      }

      target.scrollTo({
        top: 0,
        behavior: 'smooth',
      });

      // Fallbacks for compatibility
      // document.documentElement.scrollTop = 0;
      // document.body.scrollTop = 0;
    }, 100);
  }

  /**
   * Smoothly scrolls to the first thing currently blocking navigation -
   * a missing required field, or an open question whose answer fails its
   * length/value bounds check - so participants land on the question that's
   * blocking them instead of always the top of the page.
   *
   * Falls back to `scrollToTop` if nothing currently matches.
   */
  function scrollToFirstValidationIssue(root: HTMLElement | Document = document): void {
    const target = root.querySelector<HTMLElement>(
      '.required-hint.show, .invalid-length, .invalid-value'
    );
    if (!target) {
      scrollToTop();
      return;
    }

    setTimeout(() => {
      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
  }

  return {
    scrollToTop,
    scrollToFirstValidationIssue
  }
}
